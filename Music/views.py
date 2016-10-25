from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View
from django.views import generic
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.core.urlresolvers import reverse_lazy
from Music.forms import SongForm, UserForm, AlbumForm
from .models import Album, Song

AUDIO_FILE_TYPES = ['wav', 'mp3', 'ogg']
IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']


class IndexView(generic.ListView):
    template_name = 'Music/index.html'
    context_object_name = 'album_list'

    def get_queryset(self):
        return Album.objects.all()


# class Index(View):
#    template_name = 'Music/index.html'

def index(request):
    if not request.user.is_authenticated():
        return render(request, 'Music/login.html')
    else:
        song_id = []
        albums = Album.objects.filter(user=request.user)
        for album in albums:
            for song in album.song_set.all():
                song_id.append(song.pk)
        song_results = Song.objects.filter(pk__in=song_id)
        query = request.GET.get("q")
        if query:
            albums = albums.filter(
                Q(album_title__icontains=query) |
                Q(artist__icontains=query)
            ).distinct()
            song_results = song_results.filter(
                Q(song_title__icontains=query)
            ).distinct()
            return render(request, 'Music/index.html', {
                'albums': albums,
                'songs': song_results,
            })
        else:
            return render(request, 'Music/index.html', {'albums': albums})


class DetailView(generic.DetailView):
    model = Album
    template_name = 'Music/details.html'


def favorite_album(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    try:
        if album.is_favorite:
            album.is_favorite = False
        else:
            album.is_favorite = True
    except (KeyError, Album.DoesNotExist):
        return JsonResponse({'success': False})
    else:
        album.save()
    return redirect('Music:index')


def favorite_song(request, album_id, song_id):
    album = get_object_or_404(Album, pk=album_id)
    song = get_object_or_404(Song, pk=song_id)
    try:
        if song.is_favorite:
            song.is_favorite = False
        else:
            song.is_favorite = True
    except (KeyError, Song.DoesNotExist):
        return JsonResponse({'success': False})
    else:
        song.save()
        return render(request, 'Music/details.html', {'album': album})


def delete_song(request, album_id, song_id):
    album = get_object_or_404(Album, pk=album_id)
    song = get_object_or_404(Song, pk=song_id)
    song.delete()
    return render(request, 'Music/details.html', {'album': album})


class AlbumCreate(CreateView):
    model = Album
    fields = ['artist', 'album_title', 'genre', 'album_logo']


def create_album(request):
    if not request.user.is_authenticated():
        return render(request, 'Music/login.html')
    else:
        form = AlbumForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            album = form.save(commit='False')
            album.user = request.user
            album.album_logo = request.FILES['album_logo']
            file_type = album.album_logo.url.split('.')[-1]
            if file_type not in IMAGE_FILE_TYPES:
                context = {
                    'album': album,
                    'form': form,
                    'error_message': 'Image file must be PNG, JPG, or JPEG',
                }
                return render(request, 'Music/album_form.html', context)
            album.save()
            return render(request, 'Music/details.html', {'album': album})
        context = {
            'form': form,
        }
        return render(request, 'Music/album_form.html', context)


class AlbumUpdate(UpdateView):
    model = Album
    fields = ['artist', 'album_title', 'genre', 'album_logo']




class AlbumDelete(DeleteView):
    model = Album
    success_url = reverse_lazy('Music:index')

def delete_album(request,album_id):
    album = Album.objects.get(pk=album_id)
    album.delete()
    albums = Album.objects.filter(user=request.user)
    return render(request, 'Music/index.html', {'albums':albums})
'''
class SongCreate(CreateView):
    model = Song
    fields = ['album', 'song_title', 'song_ext']
'''


def create_song(request, album_id):
    form = SongForm(request.POST or None, request.FILES or None)
    album = get_object_or_404(Album, pk=album_id)
    if form.is_valid():
        albums_songs = album.song_set.all()
        for s in albums_songs:
            if s.song_title == form.cleaned_data.get("song_title"):
                context = {
                    'album': album,
                    'form': form,
                    'error_message': 'You already added that song',
                }
                return render(request, 'Music/create_song.html', context)
        song = form.save(commit=False)
        song.album = album

        song.audio_file = request.FILES['audio_file']
        file_type = song.audio_file.url.split('.')[-1]
        file_type = file_type.lower()
        if file_type not in AUDIO_FILE_TYPES:
            context = {
                'album': album,
                'form': form,
                'error_message': 'Audio file must be WAV, MP3, or OGG',
            }
            return render(request, 'Music/create_song.html', context)

        song.save()
        return render(request, 'Music/details.html', {'album': album})
    context = {
        'album': album,
        'form': form,
    }
    return render(request, 'Music/create_song.html', context)


class UserFormView(View):
    form_class = UserForm
    template_name = 'Music/registration_form.html'

    # display blank form
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    # hit submit (process form data)
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            # cleaned data
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user.set_password(password)
            user.save()

            # returns User object is credentials are correct
            user = authenticate(username=username, password=password)

            if user is not None:

                if user.is_active:
                    login(request, user)

                    # refer request.user.username etc
                    albums = Album.objects.filter(user=request.user)
                    return render(request, 'Music/index.html', {'albums': albums})

        return render(request, self.template_name, {'form': form})


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                albums = Album.objects.filter(user=request.user)
                return render(request, 'Music/index.html', {'albums': albums})
            else:
                return render(request, 'Music/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'Music/login.html', {'error_message': 'Invalid login'})
    return render(request, 'Music/login.html')


def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'Music/login.html', context)

def songs(request, filter_by):
    if not request.user.is_authenticated():
        return render(request, 'Music/login.html')
    else:
        try:
            songs_ids = []
            for album in Album.objects.filter(user=request.user):
                for song in album.song_set.all():
                    songs_ids.append(song.pk)
            user_songs = Song.objects.filter(pk__in=songs_ids)
            if filter_by == 'favorites':
                user_songs = user_songs.filter(is_favorite=True)
        except Album.DoesNotExist:
            user_songs = []
        return render(request, 'Music/songs.html', {
            'song_list':user_songs,
            'filter_by':filter_by
        })

