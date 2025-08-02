from django.shortcuts import render, redirect
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from store.models import Product, Profile
import datetime
from payment.models import PaymentOrder, PaymentOrderItem

def orders(request, pk):
	if request.user.is_authenticated:
		# Get the order (only if it belongs to the user)
		try:
			order = Order.objects.get(id=pk, user=request.user)
			# Get the order items
			items = OrderItem.objects.filter(order=pk)

			if request.POST:
				status = request.POST['shipping_status']
				# Check if true or false
				if status == "true":
					# Get the order
					order = Order.objects.filter(id=pk, user=request.user)
					# Update the status
					now = datetime.datetime.now()
					order.update(shipped=True, date_shipped=now)
				else:
					# Get the order
					order = Order.objects.filter(id=pk, user=request.user)
					# Update the status
					order.update(shipped=False)
				messages.success(request, "Shipping Status Updated")
				return redirect('home')

			return render(request, 'payment/orders.html', {"order":order, "items":items})
		except Order.DoesNotExist:
			messages.error(request, "Order not found or access denied")
			return redirect('home')
	else:
		messages.success(request, "Please log in to view your orders")
		return redirect('home')



def not_shipped_dash(request):
	if request.user.is_authenticated:
		# Filter orders to show only the logged-in user's orders
		orders = Order.objects.filter(user=request.user, shipped=False)
		if request.POST:
			status = request.POST['shipping_status']
			num = request.POST['num']
			# Get the order (only if it belongs to the user)
			order = Order.objects.filter(id=num, user=request.user)
			if order.exists():
				# grab Date and time
				now = datetime.datetime.now()
				# update order
				order.update(shipped=True, date_shipped=now)
				# redirect
				messages.success(request, "Shipping Status Updated")
				return redirect('home')
			else:
				messages.error(request, "Order not found or access denied")

		return render(request, "payment/not_shipped_dash.html", {"orders":orders})
	else:
		messages.success(request, "Please log in to view your orders")
		return redirect('home')

def shipped_dash(request):
	if request.user.is_authenticated:
		# Filter orders to show only the logged-in user's orders
		orders = Order.objects.filter(user=request.user, shipped=True)
		if request.POST:
			status = request.POST['shipping_status']
			num = request.POST['num']
			# grab the order (only if it belongs to the user)
			order = Order.objects.filter(id=num, user=request.user)
			if order.exists():
				# grab Date and time
				now = datetime.datetime.now()
				# update order
				order.update(shipped=False)
				# redirect
				messages.success(request, "Shipping Status Updated")
				return redirect('home')
			else:
				messages.error(request, "Order not found or access denied")

		return render(request, "payment/shipped_dash.html", {"orders":orders})
	else:
		messages.success(request, "Please log in to view your orders")
		return redirect('home')

def process_order(request):
	if request.POST:
		# Get the cart
		cart = Cart(request)
		cart_products = cart.get_prods
		quantities = cart.get_quants
		totals = cart.cart_total()

		# Get Billing Info from the last page
		payment_form = PaymentForm(request.POST or None)
		# Get Shipping Session Data
		my_shipping = request.session.get('my_shipping')

		# Gather Order Info
		full_name = my_shipping['shipping_full_name']
		email = my_shipping['shipping_email']
		# Create Shipping Address from session info
		shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
		amount_paid = totals

		# Create an Order
		if request.user.is_authenticated:
			# logged in
			user = request.user
			# Create Order
			create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
			create_order.save()

			# Add order items
			
			# Get the order ID
			order_id = create_order.pk
			
			# Get product Info
			for product in cart_products():
				# Get product ID
				product_id = product.id
				# Get product price
				if product.is_sale:
					price = product.sale_price
				else:
					price = product.price

				# Get quantity
				for key,value in quantities().items():
					if int(key) == product.id:
						# Create order item
						create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
						create_order_item.save()

			# Delete our cart
			for key in list(request.session.keys()):
				if key == "session_key":
					# Delete the key
					del request.session[key]

			# Delete Cart from Database (old_cart field)
			current_user = Profile.objects.filter(user__id=request.user.id)
			# Delete shopping cart in database (old_cart field)
			current_user.update(old_cart="")


			messages.success(request, "Order Placed!")
			return redirect('home')

			

		else:
			# not logged in
			# Create Order
			create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
			create_order.save()

			# Add order items
			
			# Get the order ID
			order_id = create_order.pk
			
			# Get product Info
			for product in cart_products():
				# Get product ID
				product_id = product.id
				# Get product price
				if product.is_sale:
					price = product.sale_price
				else:
					price = product.price

				# Get quantity
				for key,value in quantities().items():
					if int(key) == product.id:
						# Create order item
						create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value, price=price)
						create_order_item.save()

			# Delete our cart
			for key in list(request.session.keys()):
				if key == "session_key":
					# Delete the key
					del request.session[key]



			messages.success(request, "Order Placed!")
			return redirect('home')


	else:
		messages.success(request, "Access Denied")
		return redirect('home')

def billing_info(request):
	if request.POST:
		# Get the cart
		cart = Cart(request)
		cart_products = cart.get_prods
		quantities = cart.get_quants
		totals = cart.cart_total()

		# Create a session with Shipping Info
		my_shipping = request.POST
		request.session['my_shipping'] = my_shipping

		# Check to see if user is logged in
		if request.user.is_authenticated:
			# Get The Billing Form
			billing_form = PaymentForm()
			return render(request, "payment/billing_info.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_info":request.POST, "billing_form":billing_form})

		else:
			# Not logged in
			# Get The Billing Form
			billing_form = PaymentForm()
			return render(request, "payment/billing_info.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_info":request.POST, "billing_form":billing_form})


		
		shipping_form = request.POST
		return render(request, "payment/billing_info.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_form":shipping_form})	
	else:
		messages.success(request, "Access Denied")
		return redirect('home')


def checkout(request):
	# Get the cart
	cart = Cart(request)
	cart_products = cart.get_prods
	quantities = cart.get_quants
	totals = cart.cart_total()

	if request.user.is_authenticated:
		# Checkout as logged in user
		# Shipping User
		shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
		# Shipping Form
		shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
		return render(request, "payment/checkout.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_form":shipping_form })
	else:
		# Checkout as guest
		shipping_form = ShippingForm(request.POST or None)
		return render(request, "payment/checkout.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_form":shipping_form})

	

def payment_success(request):
	return render(request, "payment/payment_success.html", {})

def cash_delivery(request):
    if request.method == 'POST':
        try:
            # Get the cart
            cart = Cart(request)
            cart_products = cart.get_prods
            quantities = cart.get_quants
            totals = cart.cart_total()

            # Get Shipping Session Data
            my_shipping = request.session.get('my_shipping')

            # Gather Order Info
            full_name = my_shipping['shipping_full_name']
            email = my_shipping['shipping_email']
            shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
            amount_paid = totals

            # Create an Order
            if request.user.is_authenticated:
                user = request.user
                create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
                create_order.save()
                order_id = create_order.pk

                for product in cart_products():
                    product_id = product.id
                    price = product.sale_price if product.is_sale else product.price
                    for key, value in quantities().items():
                        if int(key) == product.id:
                            create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
                            create_order_item.save()

                # Clear the cart from the session
                cart.clear()
                for key in list(request.session.keys()):
                    if key == "session_key":
                        del request.session[key]

                # Update the user's profile
                current_user = Profile.objects.filter(user__id=request.user.id)
                current_user.update(old_cart="")

            else:
                create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
                create_order.save()
                order_id = create_order.pk

                for product in cart_products():
                    product_id = product.id
                    price = product.sale_price if product.is_sale else product.price
                    for key, value in quantities().items():
                        if int(key) == product.id:
                            create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value, price=price)
                            create_order_item.save()

                # Clear the cart from the session
                cart.clear()
                for key in list(request.session.keys()):
                    if key == "session_key":
                        del request.session[key]

            messages.success(request, "Order done successfully")
            return redirect('home')

        except Exception as e:
            messages.error(request, "An error occurred: " + str(e))
            return redirect('billing_info')
    return redirect('billing_info')

def process_payment_order(request):
    if request.POST:
        try:
            # Get the cart
            cart = Cart(request)
            cart_products = cart.get_prods
            quantities = cart.get_quants
            totals = cart.cart_total()

            # Get Billing Info from the last page
            payment_form = PaymentForm(request.POST, request.FILES)
            if payment_form.is_valid():
                card_name = payment_form.cleaned_data['card_name']
                card_number = payment_form.cleaned_data['card_number']
                image = payment_form.cleaned_data['image']

                # Get Shipping Session Data
                my_shipping = request.session.get('my_shipping')

                # Gather Order Info
                full_name = my_shipping['shipping_full_name']
                email = my_shipping['shipping_email']
                shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
                amount_paid = totals

                # Create an Order
                if request.user.is_authenticated:
                    # logged in
                    user = request.user
                    # Create Order
                    create_order = PaymentOrder(user=user, full_name=full_name, email=email, amount_paid=amount_paid, card_name=card_name, card_number=card_number, image=image)
                    create_order.save()

                    # Add order items
                    order_id = create_order.pk
                    for product in cart_products():
                        product_id = product.id
                        price = product.sale_price if product.is_sale else product.price
                        for key, value in quantities().items():
                            if int(key) == product.id:
                                create_order_item = PaymentOrderItem(order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
                                create_order_item.save()

                    # Clear the cart from the session
                    cart.clear()
                    for key in list(request.session.keys()):
                        if key == "session_key":
                            del request.session[key]

                    # Delete Cart from Database (old_cart field)
                    current_user = Profile.objects.filter(user__id=request.user.id)
                    current_user.update(old_cart="")

                    messages.success(request, "Order Placed!")
                    return redirect('home')

                else:
                    # not logged in
                    create_order = PaymentOrder(full_name=full_name, email=email, amount_paid=amount_paid, card_name=card_name, card_number=card_number, image=image)
                    create_order.save()

                    # Add order items
                    order_id = create_order.pk
                    for product in cart_products():
                        product_id = product.id
                        price = product.sale_price if product.is_sale else product.price
                        for key, value in quantities().items():
                            if int(key) == product.id:
                                create_order_item = PaymentOrderItem(order_id=order_id, product_id=product_id, quantity=value, price=price)
                                create_order_item.save()

                    # Clear the cart from the session
                    cart.clear()
                    for key in list(request.session.keys()):
                        if key == "session_key":
                            del request.session[key]

                    messages.success(request, "Order Placed!")
                    return redirect('home')

        except Exception as e:
            messages.error(request, "An error occurred: " + str(e))
            return redirect('billing_info')
    else:
        messages.success(request, "Access Denied")
        return redirect('home')