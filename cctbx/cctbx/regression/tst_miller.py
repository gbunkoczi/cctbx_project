from cctbx import crystal
from cctbx import miller
from cctbx import xray
from cctbx import maptbx
from cctbx.development import random_structure
from cctbx.development import debug_utils
from cctbx.array_family import flex
from scitbx.test_utils import approx_equal
import math
import sys

def exercise_set():
  xs = crystal.symmetry((3,4,5), "P 2 2 2")
  mi = flex.miller_index(((1,2,3), (0,0,4)))
  ms = miller.set(xs, mi)
  ms = miller.set(xs, mi, 00000)
  ms = miller.set(xs, mi, 0001)
  assert ms.indices() == mi
  assert ms.anomalous_flag() == 0001
  mc = ms.deep_copy()
  assert mc.unit_cell().is_similar_to(ms.unit_cell())
  assert mc.space_group() == ms.space_group()
  assert flex.order(mc.indices(), ms.indices()) == 0
  assert mc.anomalous_flag() == ms.anomalous_flag()
  assert tuple(ms.multiplicities().data()) == (4, 2)
  assert tuple(ms.epsilons().data()) == (1, 2)
  assert approx_equal(tuple(ms.d_spacings().data()), (1.177603, 1.25))
  assert approx_equal(tuple(ms.sin_theta_over_lambda_sq().data()),
                      (0.1802778, 0.16))
  assert approx_equal(ms.d_min(), 1.177603)
  assert approx_equal(ms.resolution_range(), (1.25, 1.177603))
  p1 = ms.expand_to_p1()
  assert p1.indices().size() == 6
  b = p1.setup_binner(auto_binning=0001)
  b = p1.setup_binner(reflections_per_bin=1)
  b = p1.setup_binner(n_bins=8)
  assert id(p1.binner()) == id(b)
  assert b.limits().size() == 9
  assert tuple(ms.sort().indices()) == ((0,0,4), (1,2,3))
  assert tuple(ms.sort(reverse=0001).indices()) == ((1,2,3), (0,0,4))
  ms = miller.set(xs, mi, 00000)
  mp = ms.patterson_symmetry()
  assert str(mp.space_group_info()) == "P m m m"
  assert mp.indices() == ms.indices()

def exercise_array():
  xs = crystal.symmetry((3,4,5), "P 2 2 2")
  mi = flex.miller_index(((1,-2,3), (0,0,-4)))
  data = flex.double((1,2))
  sigmas = flex.double((0.1,0.2))
  ms = miller.set(xs, mi)
  ma = miller.array(ms)
  ma = miller.array(ms, data)
  ma = miller.array(ms, data, sigmas)
  ma = miller.array(ms, data, sigmas, "test")
  assert ma.indices() == mi
  assert ma.data() == data
  assert ma.sigmas() == sigmas
  assert ma.info() == "test"
  ma.set_info("Test")
  assert ma.info() == "Test"
  ac = ma.deep_copy()
  assert flex.order(ac.data(), ma.data()) == 0
  assert flex.order(ac.sigmas(), ma.sigmas()) == 0
  assert ac.info() == None
  asu = ma.map_to_asu()
  assert tuple(asu.indices()) == ((1,2,3), (0,0,4))
  mi = flex.miller_index(((1,2,3), (-1,-2,-3), (2,3,4), (-2,-3,-4), (3,4,5)))
  data = flex.double((1,2,5,3,6))
  sigmas = flex.double((0.1,0.2,0.3,0.4,0.5))
  ms = miller.set(xs, mi, anomalous_flag=0001)
  ma = miller.array(ms, data, sigmas)
  ad = ma.anomalous_differences()
  assert tuple(ad.indices()) == ((1,2,3), (2,3,4))
  assert approx_equal(tuple(ad.data()), (-1.0, 2.0))
  assert approx_equal(tuple(ad.sigmas()), (math.sqrt(0.05), 0.5))
  for hp,hm in ((ma.hemisphere("+"), ma.hemisphere("-")), ma.hemispheres()):
    assert tuple(hp.indices()) == ((1,2,3), (2,3,4))
    assert approx_equal(tuple(hp.data()), (1,5))
    assert approx_equal(tuple(hp.sigmas()), (0.1,0.3))
    assert tuple(hm.indices()) == ((-1,-2,-3), (-2,-3,-4))
    assert approx_equal(tuple(hm.data()), (2,3))
    assert approx_equal(tuple(hm.sigmas()), (0.2,0.4))
  assert approx_equal(ma.anomalous_signal(), 0.5063697)
  ms = miller.set(crystal.symmetry(), mi, anomalous_flag=0001)
  ma = miller.array(ms, data, sigmas)
  ad = ma.anomalous_differences()
  assert tuple(ad.indices()) == ((1,2,3), (2,3,4))
  for hp,hm in ((ma.hemisphere("+"), ma.hemisphere("-")), ma.hemispheres()):
    assert tuple(hp.indices()) == ((1,2,3), (2,3,4))
    assert approx_equal(tuple(hp.data()), (1,5))
    assert approx_equal(tuple(hp.sigmas()), (0.1,0.3))
    assert tuple(hm.indices()) == ((-1,-2,-3), (-2,-3,-4))
    assert approx_equal(tuple(hm.data()), (2,3))
    assert approx_equal(tuple(hm.sigmas()), (0.2,0.4))
  assert approx_equal(ma.anomalous_signal(), 0.5063697)
  assert tuple(ma.all_selection()) == (1,1,1,1,1)
  sa = ma.apply_selection(flex.bool((1,0,0,1,0)))
  assert tuple(sa.indices()) == ((1,2,3), (-2,-3,-4))
  assert approx_equal(tuple(sa.data()), (1,3))
  assert approx_equal(tuple(sa.sigmas()), (0.1,0.4))
  ms = miller.build_set(xs, anomalous_flag=00000, d_min=1)
  ma = miller.array(ms)
  sa = ma.resolution_filter()
  assert ma.indices().size() == sa.indices().size()
  sa = ma.resolution_filter(0.5)
  assert sa.indices().size() == 0
  sa = ma.resolution_filter(d_min=2)
  assert sa.indices().size() == 10
  sa = ma.resolution_filter(d_min=2, negate=0001)
  assert sa.indices().size() == 38
  ma = ma.d_spacings()
  ma = miller.array(ma, ma.data(), ma.data().deep_copy())
  assert ma.indices().size() == 48
  sa = ma.sigma_filter(0.5)
  assert sa.indices().size() == 48
  sa = ma.sigma_filter(2)
  assert sa.indices().size() == 0
  for i in (1,13,25,27,39):
    ma.sigmas()[i] /= 3
  sa = ma.sigma_filter(2)
  assert sa.indices().size() == 5
  assert approx_equal(ma.mean(0,0), 1.6460739)
  assert approx_equal(ma.mean(0,1), 1.5146784)
  ma.setup_binner(n_bins=3)
  assert approx_equal(tuple(ma.mean(1,0)), (2.228192, 1.2579831, 1.0639812))
  assert approx_equal(tuple(ma.mean(1,1)), (2.069884, 1.2587977, 1.0779636))
  assert approx_equal(ma.mean_sq(0,0), 3.3287521)
  assert approx_equal(ma.mean_sq(0,1), 2.6666536)
  assert approx_equal(tuple(ma.mean_sq(1,0)), (5.760794, 1.5889009, 1.1336907))
  assert approx_equal(tuple(ma.mean_sq(1,1)), (4.805354, 1.5916849, 1.1629777))
  assert approx_equal(ma.rms(0,0)**2, 3.3287521)
  assert approx_equal(ma.rms(0,1)**2, 2.6666536)
  assert approx_equal([x**2 for x in ma.rms(1,0)], tuple(ma.mean_sq(1,0)))
  assert approx_equal([x**2 for x in ma.rms(1,1)], tuple(ma.mean_sq(1,1)))
  for use_binning in (0,1):
    for use_multiplicities in (0,1):
      sa = ma.rms_filter(-1, use_binning, use_multiplicities)
      assert sa.indices().size() == 0
      sa = ma.rms_filter(100, use_binning, use_multiplicities, 00000)
      assert sa.indices().size() == ma.indices().size()
      sa = ma.rms_filter(-1, use_binning, use_multiplicities, negate=0001)
      assert sa.indices().size() == ma.indices().size()
      sa = ma.rms_filter(100, use_binning, use_multiplicities, negate=0001)
      assert sa.indices().size() == 0
      sa = ma.rms_filter(1.0, use_binning, use_multiplicities)
      assert sa.indices().size() \
          == ((36, 33), (29, 29))[use_binning][use_multiplicities]
  assert approx_equal(ma.statistical_mean(), 1.380312)
  assert approx_equal(tuple(ma.statistical_mean(0001)),
                      (1.768026, 1.208446, 0.9950434))
  no = ma.remove_patterson_origin_peak()
  assert approx_equal(no.data()[0], 3.231974)
  assert approx_equal(no.data()[47], 0.004956642)
  no = ma.normalize_structure_factors()
  assert approx_equal(no.data()[0], 1.723818)
  assert approx_equal(no.data()[47], 0.6992564)
  no = ma.normalize_structure_factors(quasi=0001)
  assert approx_equal(no.data()[0], 2.4378468)
  assert approx_equal(no.data()[47], 0.9888979)
  su = ma + 3
  assert approx_equal(tuple(su.data()), tuple(ma.data() + 3))
  su = ma + ma
  assert approx_equal(tuple(su.data()), tuple(ma.data() * 2))
  assert approx_equal(tuple(su.sigmas()), tuple(ma.sigmas() * math.sqrt(2)))
  s = ma.f_as_f_sq()
  v = s.f_sq_as_f()
  assert approx_equal(tuple(ma.data()), tuple(v.data()))
  assert not approx_equal(tuple(ma.sigmas()), tuple(v.sigmas()))
  s = miller.array(ma, ma.data()).f_as_f_sq()
  v = s.f_sq_as_f()
  assert approx_equal(tuple(ma.data()), tuple(v.data()))
  assert s.sigmas() == None
  assert v.sigmas() == None
  ma = miller.array(ms)
  s = ma[:]
  assert s.data() == None
  assert s.sigmas() == None
  ma = miller.array(ms, flex.double((1,2)))
  s = ma[:]
  assert s.data().all_eq(ma.data())
  assert s.sigmas() == None
  ma = miller.array(ms, flex.double((1,2)), flex.double((3,4)))
  s = ma[:]
  assert s.data().all_eq(ma.data())
  assert s.sigmas().all_eq(ma.sigmas())
  xs = crystal.symmetry((3,4,5), "P 1 1 21")
  mi = flex.miller_index(((0,0,1), (0,0,2), (0,0,-3), (0,0,-4)))
  ms = miller.set(xs, mi)
  ma = miller.array(ms).remove_systematic_absences()
  assert tuple(ma.indices()) == ((0,0,2), (0,0,-4))
  ma = miller.array(ms).remove_systematic_absences(negate=0001)
  assert tuple(ma.indices()) == ((0,0,1), (0,0,-3))
  ma = miller.array(ms, flex.double((3,4,1,-2)), flex.double((.3,.4,.1,.2)))
  sa = ma.sort(by_value="resolution")
  assert tuple(sa.indices()) == ((0,0,1), (0,0,2), (0,0,-3), (0,0,-4))
  assert approx_equal(sa.data(), (3,4,1,-2))
  assert approx_equal(sa.sigmas(), (.3,.4,.1,.2))
  sa = ma.sort(by_value="resolution", reverse=0001)
  assert tuple(sa.indices()) == ((0,0,-4), (0,0,-3), (0,0,2), (0,0,1))
  assert approx_equal(sa.data(), (-2,1,4,3))
  assert approx_equal(sa.sigmas(), (.2,.1,.4,.3))
  sa = ma.sort(by_value="data")
  assert approx_equal(sa.data(), (4,3,1,-2))
  sa = ma.sort(by_value="data", reverse=0001)
  assert approx_equal(sa.data(), (-2,1,3,4))
  sa = ma.sort(by_value="abs")
  assert approx_equal(sa.data(), (4,3,-2,1))
  sa = ma.sort(by_value="abs", reverse=0001)
  assert approx_equal(sa.data(), (1,-2,3,4))
  sa = ma.sort(by_value=flex.double((3,1,4,2)))
  assert tuple(sa.indices()) == ((0,0,-3), (0,0,1), (0,0,-4), (0,0,2))
  sa = ma.sort(by_value=flex.double((3,1,4,2)), reverse=0001)
  assert tuple(sa.indices()) == ((0,0,2), (0,0,-4), (0,0,1), (0,0,-3))
  ma = miller.array(miller.set(xs, mi, 00000),data,sigmas).patterson_symmetry()
  assert str(ma.space_group_info()) == "P 1 1 2/m"
  assert ma.indices() == mi
  assert ma.data() == data
  assert ma.sigmas() == sigmas

def exercise_fft_map():
  xs = crystal.symmetry((3,4,5), "P 2 2 2")
  mi = flex.miller_index(((1,-2,3), (0,0,-4)))
  for anomalous_flag in (00000, 0001):
    ms = miller.set(xs, mi, anomalous_flag=anomalous_flag)
    ma = miller.array(ms, flex.complex_double((1,2)))
    fft_map = ma.fft_map()
    assert approx_equal(fft_map.resolution_factor(), 1./3)
    assert fft_map.symmetry_flags() == None
    assert approx_equal(fft_map.max_prime(), 5)
    assert fft_map.anomalous_flag() == anomalous_flag
    assert fft_map.real_map().size() > 0
    if (anomalous_flag):
      assert fft_map.complex_map().size() > 0

def exercise_squaring_and_patterson_map(space_group_info,
                                        n_scatterers=8,
                                        d_min=2,
                                        verbose=0):
  structure = random_structure.xray_structure(
    space_group_info,
    elements=["const"]*n_scatterers,
    volume_per_atom=500,
    min_distance=5.,
    general_positions_only=0001,
    u_iso=0.0)
  if (0 or verbose):
    structure.show_summary().show_scatterers()
  e_000 = math.sqrt(n_scatterers * structure.space_group().order_z())
  f_calc = structure.structure_factors(
    d_min=d_min, anomalous_flag=00000).f_calc_array()
  f_calc = f_calc.sort(by_value="abs")
  f = abs(f_calc)
  f.setup_binner(auto_binning=0001)
  e = f.normalize_structure_factors(quasi=0001)
  grid_resolution_factor = 1/3.
  u_extra = xray.calc_u_extra(d_min, grid_resolution_factor)
  if (0 or verbose):
    print "u_extra:", u_extra
  d_star_sq = e.unit_cell().d_star_sq(e.indices())
  dw = flex.exp(d_star_sq*2*(math.pi**2)*u_extra)
  eb = miller.array(miller_set=e, data=e.data()/dw)
  eb_map = eb.phase_transfer(f_calc).fft_map(
    resolution_factor=grid_resolution_factor,
    d_min=d_min,
    f_000=e_000).real_map()
  eb_map_sq = flex.pow2(eb_map)
  eb_sq = eb.structure_factors_from_map(eb_map_sq)
  mwpe = f_calc.mean_weighted_phase_error(eb_sq)
  if (0 or verbose):
    print "mean_weighted_phase_error: %.2f" % mwpe
  assert mwpe < 2
  for sharpening in (00000, 0001):
    for origin_peak_removal in (00000, 0001):
      patterson_map = eb.patterson_map(
        symmetry_flags=maptbx.use_space_group_symmetry,
        resolution_factor=grid_resolution_factor,
        f_000=e_000,
        sharpening=sharpening,
        origin_peak_removal=origin_peak_removal)
      grid_tags = maptbx.grid_tags(patterson_map.n_real())
      grid_tags.build(
        patterson_map.space_group_info().type(),
        maptbx.use_space_group_symmetry)
      assert grid_tags.n_grid_misses() == 0
      assert grid_tags.verify(patterson_map.real_map())

def run_call_back(flags, space_group_info):
  exercise_squaring_and_patterson_map(space_group_info, verbose=flags.Verbose)

def run():
  exercise_set()
  exercise_array()
  exercise_fft_map()
  debug_utils.parse_options_loop_space_groups(sys.argv[1:], run_call_back)
  print "OK"

if (__name__ == "__main__"):
  run()
