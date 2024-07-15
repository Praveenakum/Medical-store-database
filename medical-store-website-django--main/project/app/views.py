from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .models import Medicine, User, Sale, Prescription, Transaction
from .forms import UserRegisterForm, UserLoginForm, UserForm


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'app/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = UserLoginForm()
    return render(request, 'app/login.html', {'form': form})

@login_required
def home(request):
    medicines = Medicine.objects.all()
    return render(request, 'app/home.html', {'medicines': medicines})

@login_required
def medicine_detail(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST)
        prescribed_by = request.POST.get('prescribed_by')
        if form.is_valid():
            user = form.save(commit=False)
            user.medicine = medicine
            if medicine.quantity < user.quantity:
                return HttpResponse('<h1 style="color:red;background-color:black;padding:5px;text-align:center;font-size:40px;">Out of Stock</h1>')            
            user.total_price = medicine.price * user.quantity
            user.save()

            # Decrease the quantity of medicine
            medicine.quantity -= user.quantity
            medicine.save()

            # Create Sale entry
            sale = Sale(user=user, medicine=medicine, quantity_sold=user.quantity, total_price=user.total_price)
            sale.save()

            # Create Transaction entry
            transaction = Transaction(user=user, amount=user.total_price)
            transaction.save()

            # Create Prescription entry
            prescription = Prescription(user=user, prescribed_by=prescribed_by)
            prescription.save()

            return render(request, 'app/bill.html', {'user': user, 'sale': sale, 'transaction': transaction, 'prescription': prescription})
    else:
        form = UserForm()
    return render(request, 'app/medicine_detail.html', {'medicine': medicine, 'form': form})

@login_required
def search(request):
    query = request.GET.get('q')
    medicines = Medicine.objects.filter(name__icontains=query)
    if medicines:
        return render(request, 'app/search_results.html', {'medicines': medicines})
    else:
        return HttpResponse('<h1 style="color:red;background-color:black;padding:5px;text-align:center;font-size:40px;">Medicine not found</h1>')

@login_required
def create_prescription(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        prescribed_by = request.POST.get('prescribed_by')
        issue_date = request.POST.get('issue_date')
        user = get_object_or_404(User, pk=user_id)

        # Create Prescription entry
        prescription = Prescription(user=user, prescribed_by=prescribed_by, issue_date=issue_date)
        prescription.save()

        return HttpResponse('<h1 style="color:red;background-color:black;padding:5px;text-align:center;font-size:20px;">Prescription created successfully</h1>')

    else:
        return render(request, 'app/create_prescription.html')
