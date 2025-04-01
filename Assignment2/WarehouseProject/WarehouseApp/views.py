import datetime
import json
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, viewsets
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.urls import path
from django.utils.decorators import method_decorator
from .models import Item, PurchaseHeader, PurchaseDetail, PurchaseHeader, Sell, SellDetail
from .serializers import ItemSerializer, PurchaseDetailSerializer, PurchaseHeaderSerializer, SellDetailSerializer, SellSerializer
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO


# GET all items
class ItemListCreateView(generics.ListCreateAPIView):
    queryset = Item.objects.filter(is_deleted=False)
    serializer_class = ItemSerializer

# GET, UPDATE, DELETE (soft delete) item by code
class ItemDetailView(APIView):
    def get_object(self, code):
        try:
            return Item.objects.get(code=code, is_deleted=False)
        except Item.DoesNotExist:
            return None

    def get(self, request, code):
        item = self.get_object(code)
        if not item:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ItemSerializer(item)
        return Response(serializer.data)

    def put(self, request, code):
        item = self.get_object(code)
        if not item:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, code):
        item = self.get_object(code)
        if not item:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        item.is_deleted = True
        item.save()
        return Response({"message": "Item soft deleted"}, status=status.HTTP_204_NO_CONTENT)



class PurchaseHeaderListCreateView(generics.ListCreateAPIView):
    queryset = PurchaseHeader.objects.filter(is_deleted=False)
    serializer_class = PurchaseHeaderSerializer

class PurchaseHeaderDetailView(APIView):
    def get_object(self, code):
        try:
            return PurchaseHeader.objects.get(code=code, is_deleted=False)
        except PurchaseHeader.DoesNotExist:
            return None

    def get(self, request, code):
        purchase = self.get_object(code)
        if not purchase:
            return Response({"error": "Purchase not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = PurchaseHeaderSerializer(purchase)
        return Response(serializer.data)

    def put(self, request, code):
        purchase = self.get_object(code)
        if not purchase:
            return Response({"error": "Purchase not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = PurchaseHeaderSerializer(purchase, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, code):
        purchase = self.get_object(code)
        if not purchase:
            return Response({"error": "Purchase not found"}, status=status.HTTP_404_NOT_FOUND)
        purchase.is_deleted = True
        purchase.save()
        return Response({"message": "Purchase soft deleted"}, status=status.HTTP_204_NO_CONTENT)


class PurchaseDetailAPIView(APIView):
    def get(self, request, header_code):
        """Get all purchase details for a given purchase header code"""
        try:
            header = PurchaseHeader.objects.get(code=header_code)
        except PurchaseHeader.DoesNotExist:
            return Response({"error": "Purchase header not found"}, status=status.HTTP_404_NOT_FOUND)

        details = PurchaseDetail.objects.filter(header=header)
        serializer = PurchaseDetailSerializer(details, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, header_code):
        """Create purchase detail with the corresponding header_code and update stock & balance"""
        try:
            header = PurchaseHeader.objects.get(code=header_code)
        except PurchaseHeader.DoesNotExist:
            return Response({"error": "Purchase header not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data["header"] = header.id  # Assign header ID for linking

        serializer = PurchaseDetailSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 



# ViewSet for SellDetail (Detail)
class SellView(View):
    def get(self, request, code=None):
        if code:
            try:
                sell = Sell.objects.get(code=code)
                return JsonResponse({
                    'code': sell.code,
                    'date': sell.date,
                    'description': sell.description,
                }, safe=False)
            except Sell.DoesNotExist:
                return JsonResponse({'error': 'Sell not found'}, status=404)
        else:
            sells = Sell.objects.all().values('code', 'date', 'description', 'item__item_code')
            return JsonResponse(list(sells), safe=False)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            sell = Sell.objects.create(
                code=data['code'],
                date=data['date'],
                description=data['description'],
                
            )
            return JsonResponse({'message': 'Sell created successfully', 'code': sell.code})
        except Item.DoesNotExist:
            return JsonResponse({'error': 'Item not found'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def put(self, request, code):
        try:
            data = json.loads(request.body)
            sell = Sell.objects.get(code=code)
            sell.date = data.get('date', sell.date)
            sell.description = data.get('description', sell.description)
            
            sell.save()
            return JsonResponse({'message': 'Sell updated successfully'})
        except Sell.DoesNotExist:
            return JsonResponse({'error': 'Sell not found'}, status=404)
        except Item.DoesNotExist:
            return JsonResponse({'error': 'Item not found'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def delete(self, request, code):
        try:
            sell = Sell.objects.get(code=code)
            sell.delete()
            return JsonResponse({'message': 'Sell deleted successfully'})
        except Sell.DoesNotExist:
            return JsonResponse({'error': 'Sell not found'}, status=404)
        
class SellDetailViewSet(viewsets.ViewSet):
    def list(self, request, header_code=None):
        sell = get_object_or_404(Sell, code=header_code)
        details = SellDetail.objects.filter(sell=sell)
        serializer = SellDetailSerializer(details, many=True)
        return Response(serializer.data)
    
    def create(self, request, header_code=None):
        sell = get_object_or_404(Sell, code=header_code)
        item_code = request.data.get('item')
        quantity = int(request.data.get('quantity', 0))
        item = get_object_or_404(Item, code=item_code)
        
        if item.stock < quantity:
            return Response({'error': 'Not enough stock'}, status=status.HTTP_400_BAD_REQUEST)
        
        total_price = item.balance * quantity
        item.stock -= quantity
        item.save()
        
        sell_detail = SellDetail.objects.create(sell=sell, item=item, quantity=quantity, total_price=total_price)
        serializer = SellDetailSerializer(sell_detail)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    



class StockReportView(APIView):
    def get_object(self, item_code):
        """Fetch item details or return 404"""
        try:
            return Item.objects.get(code=item_code)
        except Item.DoesNotExist:
            return None

    def generate_pdf(self, html_string):
        """Generate PDF from HTML using xhtml2pdf (pisa)"""
        result = BytesIO()
        pisa_status = pisa.CreatePDF(html_string, dest=result)
        if pisa_status.err:
            return None
        return result.getvalue()

    def get(self, request, item_code):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        response_format = request.GET.get('format', 'json')  # Default JSON

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST)

        item = self.get_object(item_code)
        if not item:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

        # Fetch purchases and sales within the date range
        purchases = PurchaseDetail.objects.filter(item=item, purchase__date__range=[start_date, end_date])
        sales = SellDetail.objects.filter(item=item, sell__date__range=[start_date, end_date])

        stock_movements = []
        total_stock = 0
        total_balance = 0

        # Process purchases
        for purchase in purchases:
            total_stock += purchase.quantity
            total_balance += purchase.quantity * purchase.price_per_unit
            stock_movements.append({
                "date": purchase.purchase.date.strftime('%Y-%m-%d'),
                "description": purchase.purchase.description,
                "code": purchase.purchase.code,
                "in_qty": purchase.quantity,
                "in_price": purchase.price_per_unit,
                "in_total": purchase.quantity * purchase.price_per_unit,
                "out_qty": 0,
                "out_price": 0,
                "out_total": 0,
                "stock_qty": total_stock,
                "stock_balance": total_balance
            })

        # Process sales
        for sale in sales:
            total_stock -= sale.quantity
            total_balance -= sale.total_price
            stock_movements.append({
                "date": sale.sell.date.strftime('%Y-%m-%d'),
                "description": sale.sell.description,
                "code": sale.sell.code,
                "in_qty": 0,
                "in_price": 0,
                "in_total": 0,
                "out_qty": sale.quantity,
                "out_price": sale.total_price / sale.quantity if sale.quantity else 0,
                "out_total": sale.total_price,
                "stock_qty": total_stock,
                "stock_balance": total_balance
            })

        report_data = {
            "item": {
                "code": item.code,
                "name": item.name,
                "unit": item.unit
            },
            "transactions": stock_movements,
            "summary": {
                "total_in": sum(p["in_qty"] for p in stock_movements),
                "total_out": sum(p["out_qty"] for p in stock_movements),
                "final_stock": total_stock,
                "final_balance": total_balance
            }
        }

        # Return JSON response
        if response_format == 'json':
            return Response(report_data)

        # Generate PDF using xhtml2pdf (pisa)
        html_string = render_to_string('stock_report_template.html', {'report': report_data})
        pdf_file = self.generate_pdf(html_string)

        if pdf_file is None:
            return Response({"error": "Failed to generate PDF"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="stock_report_{item_code}.pdf"'
        return response
