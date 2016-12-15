from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url('rest/convert', views.convert_files, name='convert_files'),
    url('rest/symmetry', views.analyze_symmetry, name='analyze_symmetry'),
    url('rest/xrd', views.calculate_xrd, name='calculate_xrd'),
    url('rest/surfaces', views.generate_surfaces, name='generate_surfaces'),
    url('rest/compare', views.compare_structures, name='compare_structures'),
]
