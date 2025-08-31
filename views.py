from django.contrib import messages
from django.shortcuts import render, HttpResponse
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
# Create your views here.
from users.forms import UserRegistrationForm
from .models import UserRegistrationModel,ImageModel
from diffusers import StableDiffusionPipeline
import torch
from PIL import Image


def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            print('Data is Valid')
            form.save()
            messages.success(request, 'You have been successfully registered')
            form = UserRegistrationForm()
            return render(request, 'UserRegistrations.html', {'form': form})
        else:
            messages.success(request, 'Email or Mobile Already Existed')
            print("Invalid form")
    else:
        form = UserRegistrationForm()
    return render(request, 'UserRegistrations.html', {'form': form})


def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        print("Login ID = ", loginid, ' Password = ', pswd)
        try:
            check = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            status = check.status
            print('Status is = ', status)
            if status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid
                request.session['email'] = check.email
                print("User id At", check.id, status)
                return render(request, 'users/UserHomePage.html', {})
            else:
                messages.success(request, 'Your Account Not at activated')
                return render(request, 'UserLogin.html')
        except Exception as e:
            print('Exception is ', str(e))
            pass
        messages.success(request, 'Invalid Login id and password')
    return render(request, 'UserLogin.html', {})


def UserHome(request):
    user_name=request.session['loginid']
    print(user_name)
    return render(request, 'users/UserHomePage.html', {})

import os
import torch
from django.shortcuts import render
from django.conf import settings
from datetime import datetime
from .models import ImageModel
from diffusers import StableDiffusionPipeline

def test_text_to_image(request):
    if request.method == "POST":
        description = request.POST.get('description', '').strip()
        u_name = request.session.get('loginid', 'Guest')  # Ensure loginid exists

        print("Description is:", description)

        # Load the pre-trained Stable Diffusion model
        model_id = "CompVis/stable-diffusion-v1-4"
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Initialize the pipeline
        pipe = StableDiffusionPipeline.from_pretrained(model_id).to(device)

        # Generate image from text
        def generate_image_from_text(prompt, num_inference_steps=50, guidance_scale=7.5):
            with torch.autocast(device):
                image = pipe(prompt, num_inference_steps=num_inference_steps, guidance_scale=guidance_scale).images[0]
            return image

        generated_image = generate_image_from_text(description)

        # Generate a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"generated_{timestamp}.png"
        image_path = os.path.join(settings.MEDIA_ROOT, 'generated_images', image_filename)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(image_path), exist_ok=True)

        # Save the image
        generated_image.save(image_path)

        # Save image entry in the database
        image_record = ImageModel.objects.create(
            username=u_name,
            text_description=description,
            image_generated=f"generated_images/{image_filename}"
        )

        return render(request, "users/test_form_result.html", {
            "path": image_record.image_generated.url,
            "text": description,
            "time": image_record.date_now
        })
    
    return render(request, "users/test_form.html", {})



def Leaf_Predictions(request):
    if request.method == 'POST':
        myfile = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        # from .utility import leafPredictionModel
        # result, test_img = leafPredictionModel.predict_leaf(filename)
        path = os.path.join(settings.MEDIA_ROOT, filename)
        result = script.analysis(path)
        print('Result:', result)
        return render(request, "users/leaf_form.html", {"result": result, "path": uploaded_file_url})
    else:
        return render(request, "users/leaf_form.html", {})
