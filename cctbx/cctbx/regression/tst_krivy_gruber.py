from cctbx.uctbx import reduction_base
from cctbx.uctbx import krivy_gruber_1976
from cctbx.uctbx import gruber_1973_table_1
from cctbx import uctbx
from cctbx import sgtbx
from cctbx import matrix
from scitbx.python_utils.misc import time_log
from scitbx.test_utils import approx_equal
import math
import random
import sys

class check_is_niggli_cell(reduction_base.gruber_parameterization):

  def itva_is_niggli_cell(self):
    eq = self.eps_eq
    gt = self.eps_gt
    a,b,c,d,e,f = (self.a,self.b,self.c,self.d,self.e,self.f)
    if (not self.meets_main_conditions()): return 00000
    type = self.type()
    assert type in (1,2)
    if (type == 1):
      if (eq(a, b)):
        if (gt(d, e)): return 00000
      if (eq(b, c)):
        if (gt(e, f)): return 00000
      if (eq(d, b)):
        if (gt(f, 2*e)): return 00000
      if (eq(e, a)):
        if (gt(f, 2*d)): return 00000
      if (eq(f, a)):
        if (gt(e, 2*d)): return 00000
    else:
      if (eq(a, b)):
        if (gt(abs(d), abs(e))): return 00000
      if (eq(b, c)):
        if (gt(abs(e), abs(f))): return 00000
      if (eq(abs(d), b)):
        if (not eq(f, 0)): return 00000
      if (eq(abs(e), a)):
        if (not eq(f, 0)): return 00000
      if (eq(abs(f), a)):
        if (not eq(e, 0)): return 00000
      if (eq(abs(d)+abs(e)+abs(f), a+b)):
        if (gt(a, abs(e) + abs(f)/2)): return 00000
    return 0001

relative_epsilon = None

time_reduce = time_log("krivy_gruber_1976.reduction")

def reduce(inp):
  time_reduce.start()
  red = krivy_gruber_1976.reduction(inp, relative_epsilon=relative_epsilon)
  time_reduce.stop()
  assert red.is_niggli_cell()
  if (relative_epsilon is None):
    assert check_is_niggli_cell(red.as_unit_cell()).itva_is_niggli_cell()
  return red

def ucgmx((a,b,c,d,e,f)): # unit cell given Gruber matrix
  return uctbx.unit_cell((a,b,c,f/2.,e/2.,d/2.), is_metrical_matrix=0001)

def exercise_gruber_1973_example():
  start = ucgmx((4,136,76,-155,-31,44))
  assert start.is_similar_to(uctbx.unit_cell(
    (2, 11.66, 8.718, 139+40/60., 152+45/60., 19+24/60.)))
  buerger = ucgmx((4,16,16,-16,-1,-3))
  assert buerger.is_similar_to(uctbx.unit_cell(
    (2, 4, 4, 120, 93.5833, 100.807)))
  niggli = ucgmx((4,16,16,16,3,4))
  assert niggli.is_similar_to(uctbx.unit_cell(
    (2, 4, 4, 60, 79.1931, 75.5225)))
  red = reduction_base.gruber_parameterization(start)
  assert not red.is_buerger_cell()
  assert approx_equal(red.as_gruber_matrix(), (4,136,76,-155,-31,44))
  assert approx_equal(red.as_niggli_matrix(), (4,136,76,-155/2.,-31/2.,44/2.))
  assert approx_equal(red.as_sym_mat3(), (4,136,76,44/2.,-31/2.,-155/2.))
  assert red.as_unit_cell().is_similar_to(start)
  red = reduction_base.gruber_parameterization(buerger)
  assert red.is_buerger_cell()
  assert not red.is_niggli_cell()
  red = reduction_base.gruber_parameterization(niggli)
  assert red.is_niggli_cell()
  red = reduce(start)
  assert red.as_unit_cell().is_similar_to(niggli)
  assert red.r_inv().elems == (-1, 5, 9, 0, -1, -1, 0, 0, 1)
  assert red.n_iterations() == 19
  red = reduce(buerger)
  assert red.as_unit_cell().is_similar_to(niggli)
  assert red.r_inv().elems == (-1, 0, 0, 0, 1, 1, 0, 1, 0)
  assert red.n_iterations() == 3
  red = reduce(niggli)
  assert red.as_unit_cell().is_similar_to(niggli)
  assert red.r_inv().elems == (1, 0, 0, 0, 1, 0, 0, 0, 1)
  assert red.n_iterations() == 1
  try:
    red = krivy_gruber_1976.reduction(buerger, iteration_limit=1)
  except krivy_gruber_1976.iteration_limit_exceeded, e:
    pass
  else:
    raise RuntimeError, "Exception expected."
  assert not start.is_buerger_cell()
  assert not start.is_niggli_cell()
  assert buerger.is_buerger_cell()
  assert not buerger.is_niggli_cell()
  assert niggli.is_buerger_cell()
  assert niggli.is_niggli_cell()
  red = start.niggli_reduction()
  assert red.n_iterations() == 19
  assert start.niggli_cell().is_similar_to(niggli)

def exercise_krivy_gruber_1976_example():
  start = ucgmx((9,27,4,-5,-4,-22))
  assert start.is_similar_to(uctbx.unit_cell(
    (3, 5.196, 2, 103+55/60., 109+28/60., 134+53/60.)))
  for gmx in ((4,9,9,-8,-1,-4),
              (4,9,9,9,1,4)):
    red = reduction_base.gruber_parameterization(ucgmx(gmx))
    assert red.is_buerger_cell()
    assert not red.is_niggli_cell()
  niggli = ucgmx((4,9,9,9,3,4))
  assert niggli.is_similar_to(uctbx.unit_cell(
    (2, 3, 3, 60, 75+31/60., 70+32/60.)))
  red = reduction_base.gruber_parameterization(niggli)
  assert red.is_niggli_cell()
  red = reduce(start)
  assert red.as_unit_cell().is_similar_to(niggli)
  assert red.r_inv().elems == (0, 1, 2, 0, 0, 1, 1, 1, 2)
  assert red.n_iterations() == 6

def exercise_bravais_plus():
  for pg in ("1", "2", "2 2", "4", "3*", "6", "2 2 3"):
    for z in "PABCIRF":
      sgi = sgtbx.space_group_info("Hall: %s %s" % (z, pg))
      r_inv = sgi.group().z2p_op().c_inv().r()
      reduce(sgi.any_compatible_unit_cell(volume=100).change_basis(
        r_inv.num(),r_inv.den()))

def cos_deg(x):
  return math.cos(x*math.pi/180)

def exercise_grid(quick=00000, verbose=0):
  if (quick):
    sample_lengths = (10,)
    sample_angles = (60,)
  else:
    sample_lengths = (10,20,30)
    sample_angles = (10,30,45,60,90,120,150,170)
  n_trials = 0
  for a in sample_lengths:
    for b in sample_lengths:
      for c in sample_lengths:
        for alpha in sample_angles:
          for beta in sample_angles:
            for gamma in sample_angles:
              a_b = a*b*cos_deg(gamma)
              a_c = a*c*cos_deg(beta)
              b_c = b*c*cos_deg(alpha)
              g = matrix.sqr((a*a,a_b,a_c,
                              a_b,b*b,b_c,
                              a_c,b_c,c*c))
              det_g = g.determinant()
              try: unit_cell = uctbx.unit_cell((a,b,c,alpha,beta,gamma))
              except:
                assert det_g <= 1.e-5
                continue
              assert abs(det_g-unit_cell.volume()**2) < 1.e-5
              if (unit_cell.volume() < a*b*c/1000): continue
              n_trials += 1
              reduce(unit_cell)
  if (0 or verbose):
    print "exercise_grid n_trials:", n_trials

class random_unimodular_integer_matrix_generator:

  def __init__(self, reset_threshold=10):
    self.reset_threshold = reset_threshold
    self._m1 = matrix.sqr((0,0,1,1,0,0,0,1,0))
    self._m2 = matrix.sqr((1,-1,0,1,0,0,0,0,1))
    self._mi = self._m1 * self._m2

  def has_elements_which_are_to_large(self):
    e = self._mi.elems
    return max(abs(min(e)), abs(max(e))) >= self.reset_threshold

  def next(self):
    while 1:
      if (random.randrange(0,2)):
        self._mi = self._m2 * self._mi
      else:
        self._mi = self._m1 * self._mi
      if (not self.has_elements_which_are_to_large()):
        break
      self._mi = random.choice((self._m1, self._m2))
    return self._mi

class random_abcpq:

  def __init__(self, ck_type):
    rr = random.randrange
    self.a = rr(100,201)
    self.b = self.a
    self.p = rr(10,41)
    self.q = self.a
    if (ck_type[0] == "q"):
      if (ck_type[1] != "=" and rr(0,2)):
        self.q = rr(50,91)
      ck_type = ck_type[2:]
    if   (ck_type == "a=b<=c"):
      self.c = self.b
      if (rr(0,2)): self.c += rr(10,101)
    elif (ck_type == "a<b=c"):
      self.b += rr(10,101)
      self.c = self.b
    elif (ck_type == "a<=b<c"):
      if (rr(0,2)): self.b += rr(10,101)
      self.c = self.b + rr(10,101)
    elif (ck_type == "a<b<c"):
      self.b += rr(10,101)
      self.c = self.b + rr(10,101)
    elif (ck_type == "a=b<c"):
      self.c = self.b + rr(10,101)
    elif (ck_type == "a<b<=c"):
      self.b += rr(10,101)
      self.c = self.b
      if (rr(0,2)): self.c += rr(10,101)
    else:
      raise RuntimeError, "Unknown ck_type."

  def eval_defks(self, defks):
    a,b,c,p,q = tuple([float(x) for x in (self.a,self.b,self.c,self.p,self.q)])
    m = b/a
    n = (b-a)/a
    d,e,f = eval(defks)
    return a,b,c,d,e,f

def random_gruber_matrix(type_conditions):
  return random_abcpq(random.choice(
    type_conditions.ck_types)).eval_defks(type_conditions.defks)

def exercise_gruber_types(n_trials_per_type, verbose=0):
  mk2_sets = gruber_1973_table_1.get_mk2_sets()
  type_conditions = gruber_1973_table_1.get_type_conditions()
  random_unimodular = random_unimodular_integer_matrix_generator()
  have_errors = 00000
  for k in xrange(1,29):
    set = mk2_sets[k]
    tc = type_conditions[k]
    if (0 or verbose):
      print " ", tc.ck_types, tc.defks
    n_errors = 0
    for i_trial in xrange(n_trials_per_type):
      gruber_matrix = random_gruber_matrix(tc)
      type_cell = ucgmx(gruber_matrix)
      if (0 or verbose):
        print " ", gruber_matrix
        print " ", type_cell
      red = reduction_base.gruber_parameterization(type_cell)
      assert red.is_niggli_cell()
      n_different_cells = 0
      for m in set:
        other_cell = type_cell.change_basis(m.inverse().transpose().elems, 1)
        if (0 or verbose):
          print " ", m.elems, m.determinant()
          print " ", other_cell
        red = reduction_base.gruber_parameterization(other_cell)
        if (not red.is_buerger_cell()):
          print "  Error: Transformed cell is not a Buerger cell."
          print "  gruber_matrix:", gruber_matrix
          n_errors += 1
        else:
          n_different_cells += 1
          if (red.is_niggli_cell()):
            if (not other_cell.is_similar_to(type_cell)):
              print "  Error: Transformed cell is a Niggli cell."
              print "  gruber_matrix:", gruber_matrix
              n_errors += 1
          else:
            krivy_cell = reduce(type_cell).as_unit_cell()
            assert krivy_cell.is_similar_to(type_cell)
            krivy_cell = reduce(other_cell).as_unit_cell()
            assert krivy_cell.is_similar_to(type_cell)
            r_inv = random_unimodular.next().elems
            random_cell = type_cell.change_basis(r_inv, 1)
            if (0 or verbose):
              print "  Random:", random_cell, r_inv
            red = reduce(random_cell)
            krivy_cell = red.as_unit_cell()
            if (not krivy_cell.is_similar_to(type_cell)):
              print "  Error: Random cell recovery."
              print "  gruber_matrix:", gruber_matrix
              print "  r_inv:", r_inv
              print "  red.as_gruber_matrix():", red.as_gruber_matrix()
              n_errors += 1
      if (n_different_cells == 0):
        print "  Error: Transformation does not yield different cells."
        n_errors += 1
        raise RuntimeError
    if ((0 or verbose) and n_errors != 0):
      print "Errors for type %d:" % k, n_errors
    if (n_errors != 0):
      have_errors = 0001
  assert not have_errors

def exercise_extreme():
  uc = uctbx.unit_cell((
    69.059014477286041, 48.674386086971339, 0.0048194797114296736,
    89.995145576185806, 89.999840576946085, 99.484656090034875))
  try:
    uc.niggli_reduction()
  except krivy_gruber_1976.extreme_unit_cell:
    pass
  else:
    raise RuntimeError, "Exception expected."
  uc = uctbx.unit_cell((
    80.816186392181365, 81.021289502648813, 140.6784408482614,
    29.932540128999769, 89.92047105556459, 119.85301114570319))
  uc.niggli_reduction(iteration_limit=10000)

def exercise_real_world_examples():
  # SSZ-59, cell by Michael Treacy, infinite loop in GSAS rducll (Linux)
  uc = uctbx.unit_cell((
    12.7366, 29.2300, 5.0242,
    94.6570, 100.8630, 99.7561))
  nc = uc.niggli_cell()
  assert nc.is_similar_to(uctbx.unit_cell(
    (5.0242, 12.7366, 29.23, 99.7561, 94.657, 100.863)))
  # SSZ-59, Burton et al., Table 4
  uc = uctbx.unit_cell((
    12.7806, 12.7366, 29.457,
    103.42, 103.57, 22.71))
  red = uc.niggli_reduction()
  assert red.as_unit_cell().is_similar_to(nc)
  assert red.r_inv().elems == (-1, 0, 1, 1, -1, 0, 0, 0, 1)

def exercise():
  exercise_extreme()
  quick = "--Quick" in sys.argv[1:]
  verbose = "--Verbose" in sys.argv[1:]
  exercise_gruber_1973_example()
  exercise_krivy_gruber_1976_example()
  if ("--zero_epsilon" in sys.argv[1:]):
    global relative_epsilon
    relative_epsilon = 0
  exercise_bravais_plus()
  exercise_grid(quick=quick, verbose=verbose)
  if (quick): n_trials_per_type=10
  else:       n_trials_per_type=100
  exercise_gruber_types(n_trials_per_type, verbose)
  exercise_real_world_examples()
  if (0 or verbose):
    print time_reduce.report()
  print "OK"

if (__name__ == "__main__"):
  exercise()
