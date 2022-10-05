from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from ads.models import Ad,  Comment, Fav
from ads.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView
from django.db.models import Q

from ads.forms import CreateForm, CommentForm


class AdListView(OwnerListView):
    model = Ad
    # By convention:
    template_name = "ads/ad_list.html"

    def get(self, request) :
        strval =  request.GET.get("search", False)
        if strval :
            query = Q(title__icontains=strval)
            query.add(Q(text__icontains=strval), Q.OR)
            query.add(Q(price__icontains=strval), Q.OR)
            ad_list = Ad.objects.filter(query).select_related().order_by('-updated_at')[:10]
        else:
            ad_list = Ad.objects.all()
        favorites = list()
        if request.user.is_authenticated:
            # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
            rows = request.user.favorite_ads.values('id')
            # favorites = [2, 4, ...] using list comprehension
            favorites = [ row['id'] for row in rows ]
        ctx = {'ad_list' : ad_list, 'favorites': favorites}
        return render(request, self.template_name, ctx)


class AdDetailView(OwnerDetailView):
    model = Ad
    template_name = "ads/ad_detail.html"
    def get(self, request, pk) :
        x = Ad.objects.get(id=pk)
        comments = Comment.objects.filter(ad=x).order_by('-updated_at')
        comment_form = CommentForm()
        context = { 'ad' : x, 'comments': comments, 'comment_form': comment_form }
        return render(request, self.template_name, context)

class AdCreateView(LoginRequiredMixin, View):
    # List the fields to copy from the Article model to the Article form
    #fields = ['title', 'price', 'text']
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('ads:all')
    def get(self, request, pk=None):
        form = CreateForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = CreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        ads = form.save(commit=False)
        ads.owner = self.request.user
        ads.save()
        return redirect(self.success_url)

class AdUpdateView(LoginRequiredMixin, View):
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('ads:all')

    def get(self, request, pk):
        ads = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(instance=ads)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        ads = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(request.POST, request.FILES or None, instance=ads)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        ads = form.save(commit=False)
        ads.save()

        return redirect(self.success_url)


class AdDeleteView(OwnerDeleteView):
    model = Ad

def AdStream_file(request, pk):
    ad = get_object_or_404(Ad, id=pk)
    response = HttpResponse()
    response['Content-Type'] = ad.content_type
    response['Content-Length'] = len(ad.picture)
    response.write(ad.picture)
    return response

class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        f = get_object_or_404(Ad, id=pk)
        comment = Comment(text=request.POST['comment'], owner=request.user, ad=f)
        comment.save()
        return redirect(reverse('ads:ad_detail', args=[pk]))

class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "ads/comment_delete.html"

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Add PK",pk)
        t = get_object_or_404(Ad, id=pk)
        fav = Fav(user=request.user, ad=t)
        try:
            fav.save()  # In case of duplicate key
        except IntegrityError as e:
            pass
        return HttpResponse()

@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Delete PK",pk)
        t = get_object_or_404(Ad, id=pk)
        try:
            fav = Fav.objects.get(user=request.user, ad=t).delete()
        except Fav.DoesNotExist as e:
            pass

        return HttpResponse()

