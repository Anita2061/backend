import hmac
import hashlib
import base64
import uuid
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignupSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_esewa_payment(request):
    amount = request.data.get('amount')
    items = request.data.get('items', [])
    name = request.data.get('name')
    phone = request.data.get('phone')
    location = request.data.get('location')

    print(f"DEBUG: eSewa payment initiated for amount: {amount} by user {request.user.username}")
    
    transaction_uuid = str(uuid.uuid4())
    product_code = "EPAYTEST"
    secret_key = "8gBm/:&EnhH.1/q" 

    # Create a pending order in MongoDB
    try:
        from .services import create_order
        # We pass status="pending" or handle it in create_order. 
        # By default create_order sets "pending".
        create_order(str(request.user.id), items, name, phone, location, float(amount))
    except Exception as e:
        print(f"Failed to create pending order for eSewa: {e}")
        # We continue anyway to let the user pay, or we could return error.
        # Better to have the order record.

    data_to_sign = f"total_amount={amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    
    secret_key_bytes = secret_key.encode('utf-8')
    data_bytes = data_to_sign.encode('utf-8')
    
    hash_obj = hmac.new(secret_key_bytes, data_bytes, hashlib.sha256)
    signature = base64.b64encode(hash_obj.digest()).decode('utf-8')

    return Response({
        "signature": signature,
        "transaction_uuid": transaction_uuid,
        "amount": amount,
        "product_code": product_code
    })

@api_view(['POST'])
def signup(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not email or not password:
        return Response({"detail": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

    # 1. Check if user already exists in Django (SQL)
    if User.objects.filter(username=username).exists():
        return Response({"detail": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(email=email).exists():
        return Response({"detail": "Email already registered."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 2. Create in Django (SQL) for JWT Auth
        user = User.objects.create_user(username=username, email=email, password=password)

        # 3. Create in MongoDB (for Product/Cart management)
        try:
            from .services import create_user_in_mongo
            create_user_in_mongo(name=username, email=email, password=password, django_id=str(user.id))
        except Exception as mongo_err:
            user.delete()
            print(f"MongoDB User Creation Failed: {mongo_err}")
            return Response({"detail": f"Database Sync Error: Please check MongoDB connection. {mongo_err}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        refresh = RefreshToken.for_user(user)
        return Response({
            "token": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        print(f"Signup error: {e}")
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {"detail": "Email and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Django's User model authenticates by username, so look up the user by email first
    try:
        user_obj = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {"detail": "Invalid email or password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    user = authenticate(username=user_obj.username, password=password)

    if user is None:
        return Response(
            {"detail": "Invalid email or password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    refresh = RefreshToken.for_user(user)

    return Response({
        "token": str(refresh.access_token),
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    })

from .services import get_cart, set_cart, create_order
from core.mongo import carts_collection, serialize_mongo_doc, user_collection, orders_collection, products_collection

@api_view(['GET'])
def get_products_view(request):
    try:
        products = list(products_collection.find())
        return Response([serialize_mongo_doc(p) for p in products])
    except Exception as e:
        print(f"Failed to fetch products: {e}")
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order_view(request):
    print(f"DEBUG: Received checkout request for user {request.user.username}")
    print(f"DEBUG: Request data: {request.data}")
    user_id = str(request.user.id)
    items = request.data.get('items', [])
    name = request.data.get('name')
    phone = request.data.get('phone')
    location = request.data.get('location')
    total = request.data.get('total', 0)

    if not items or not name or not phone or not location:
        print("DEBUG: Missing order information")
        return Response({"detail": "Missing order information."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        order = create_order(user_id, items, name, phone, location, total)
        print(f"DEBUG: Order created successfully: {order}")
        return Response(order, status=status.HTTP_201_CREATED)
    except Exception as e:
        import traceback
        print(f"Order creation failed: {e}")
        traceback.print_exc()
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders_view(request):
    user_id = str(request.user.id)
    try:
        orders = list(orders_collection.find({"user_id": user_id}).sort("created_at", -1))
        return Response([serialize_mongo_doc(o) for o in orders])
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart_view(request):
    user_id = str(request.user.id)
    cart = get_cart(user_id)
    return Response(cart)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_cart_view(request):
    user_id = str(request.user.id)
    items = request.data.get('items', [])
    cart = set_cart(user_id, items)
    return Response(cart)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    return Response({
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    })
    
    