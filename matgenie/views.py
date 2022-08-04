# Create your views here.

import json
import itertools

from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseBadRequest,\
    HttpResponseForbidden, JsonResponse

from monty.json import MontyEncoder, MontyDecoder
try:
    from io import StringIO
except ImportError:
    from cStringIO import StringIO

from pymatgen.core import Structure
from pymatgen.core import __version__ as PYMATGEN_VERSION
from pymatgen.io.vasp import Poscar
from pymatgen.io.cif import CifParser, CifWriter
from pymatgen.io.cssr import Cssr
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pymatgen.analysis.structure_matcher import StructureMatcher
from pymatgen.core.surface import SlabGenerator
from pymatgen.analysis.diffraction.xrd import XRDCalculator
from django.views.decorators.csrf import csrf_exempt

import matplotlib
matplotlib.use("pdf")

def index(request):
    return render(request, 'templates/index.html', {"pmg_version": PYMATGEN_VERSION})


def rest_func(supported_methods=("GET", )):
    """
    Decorator to standardize api checks and handle responses.

    Args:
        supported_methods (list): List of supported methods. E.g., ["GET"],
            ["GET", "POST"].

    Returns:
        JsonResponse or HttpResponseBadRequest
    """
    def wrap(func):
        def wrapped(*args, **kwargs):
            request = args[0]
            method = getattr(request, request.method.upper())
            try:
                if request.method not in supported_methods:
                    raise PermissionDenied("Invalid request method.")
                results = func(*args, **kwargs)
                return JsonResponse({"results" :results})
            except PermissionDenied as ex:
                return JsonResponse({"error": str(ex.message)})
            except Exception as ex:
                import traceback
                tbstr = traceback.format_exc()
                return HttpResponseBadRequest(
                    json.dumps({"error": str(ex.message)}), content_type="application/json")
        return wrapped
    return wrap


@csrf_exempt
@rest_func(supported_methods=("POST", ))
def convert_files(request):
    fmt = request.POST["output-format"]
    results = {}
    for name, f in request.FILES.items():
        name, s = get_structure(f)
        results[name] = s.to(fmt=fmt)
    return results


@csrf_exempt
@rest_func(supported_methods=("POST", ))
def analyze_symmetry(request):
    results = {}
    symprec = float(request.POST["symprec"])
    angle_tolerance = float(request.POST["angle_tolerance"])
    for name, f in request.FILES.items():
        name, s = get_structure(f)
        a = SpacegroupAnalyzer(s, symprec=symprec, angle_tolerance=angle_tolerance)
        d = {}
        d["international"] = a.get_space_group_symbol()
        d["number"] = a.get_space_group_number()
        d["hall"] = a.get_hall()
        d["point_group"] = a.get_point_group()
        d["crystal_system"] = a.get_crystal_system()
        results[name] = d
    return results


@csrf_exempt
@rest_func(supported_methods=("POST", ))
def generate_surfaces(request):
    f = list(request.FILES.values())[0]
    name, s = get_structure(f)
    miller = [int(i) for i in request.POST["miller"].split(",")]
    if len(miller) != 3:
        raise ValueError("Invalid miller index!")
    vac_size = float(request.POST["vac-size"])
    slab_size = float(request.POST["slab-size"])
    fmt = request.POST["output-format"]
    gen = SlabGenerator(s, miller_index=miller,
                        min_slab_size=slab_size,
                        min_vacuum_size=vac_size)
    slabs = gen.get_slabs(bonds={})
    results = [sl.to(fmt=fmt) for sl in slabs]
    return results


@csrf_exempt
@rest_func(supported_methods=("POST", ))
def compare_structures(request):
    structures = dict([get_structure(f) for name, f in request.FILES.items()])
    a = StructureMatcher()
    results = []
    for n1, n2 in itertools.combinations(structures.keys(), 2):
        s1 = structures[n1]
        s2 = structures[n2]
        d = a.get_rms_anonymous(s1, s2)
        if d[0] is not None:
            r = {"rms": d[0], "match_found": True,
                 "mapping": {str(k): str(v) for k, v in d[1].items()}}
        else:
            r = {"match_found": False, "mapping": None, "rms": None}
        r["files"] = [n1, n2]
        results.append(r)
    return results


@csrf_exempt
@rest_func(supported_methods=("POST", ))
def calculate_xrd(request):
    results = {}
    xrd = XRDCalculator(symprec=0.01)
    for name, f in request.FILES.items():
        name, s = get_structure(f)
        plt = xrd.get_xrd_plot(s, annotate_peaks=False)
        fig = plt.gcf()
        fig.set_dpi(100)
        fig.set_size_inches(8, 6)
        ax = plt.gca()
        plt.setp(ax.get_xticklabels(), fontsize=16)
        plt.setp(ax.get_yticklabels(), fontsize=16)
        ax.xaxis.label.set_size(16)
        ax.yaxis.label.set_size(16)

        si = StringIO()
        plt.savefig(si, format="svg")
        results[name] = si.getvalue()
    return results


def get_structure(f):
    name = f.name
    content = f.read()
    content = content.decode("utf-8")
    if "POSCAR" in name or "CONTCAR" in  name:
        s = Poscar.from_string(content, False).structure
    elif ".cif" in name.lower():
        parser = CifParser.from_string(content)
        s = parser.get_structures(False)[0]
    elif ".cssr" in name.lower():
        cssr = Cssr.from_string(content)
        s = cssr.structure
    elif ".mson" in name.lower():
        s = json.loads(content, cls=MontyDecoder)
        if type(s) != Structure:
            raise IOError("File does not contain a valid serialized "
                          "structure")
    else:
        raise ValueError(name + " is an invalid file format. Only "
                               "POSCAR, CIF, CSSR and MSON (Materials "
                               "Project JSON) are supported right now.")
    return name, s
