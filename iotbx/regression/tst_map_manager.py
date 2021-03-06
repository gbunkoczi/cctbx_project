from __future__ import absolute_import, division, print_function
import os
from iotbx.data_manager import DataManager
from iotbx.map_manager import map_manager
from libtbx.test_utils import approx_equal

def test_01():

  data_dir = os.path.dirname(os.path.abspath(__file__))
  data_ccp4 = os.path.join(data_dir, 'data',
                          'non_zero_origin_map.ccp4')
  data_pdb = os.path.join(data_dir, 'data',
                          'non_zero_origin_map.ccp4')

  dm = DataManager(['miller_array','real_map', 'phil'])
  dm.set_overwrite(True)
  dm.process_real_map_file(data_ccp4)

  # test writing and reading file
  mm = dm.get_real_map()
  mm.shift_origin()
  mm.show_summary()
  dm.write_real_map_file(mm, filename='test_map_manager.ccp4', overwrite=True)
  os.remove('test_map_manager.ccp4')

  # test writing and reading file without shifting origin
  dm = DataManager(['miller_array','real_map', 'phil'])
  dm.set_overwrite(True)
  dm.process_real_map_file(data_ccp4)
  mm = dm.get_real_map()
  mm.show_summary()
  dm.write_real_map_file(mm, filename='test_map_manager.ccp4', overwrite=True)

  new_mm=map_manager('test_map_manager.ccp4')
  assert (new_mm.is_similar(mm))
  new_mm.shift_origin()
  assert (not new_mm.is_similar(mm))

  # get map_data
  mm.shift_origin()
  map_data=mm.map_data()
  assert approx_equal(map_data[15,10,19], 0.38,eps=0.01)

  # get crystal_symmetry
  cs=mm.crystal_symmetry()
  assert approx_equal(cs.unit_cell().parameters()[0] ,22.41,eps=0.01)

  # and full cell symmetry
  full_cs=mm.unit_cell_crystal_symmetry()
  assert approx_equal(full_cs.unit_cell().parameters()[0] ,149.4066,eps=0.01)

  # write map directly:
  mm.write_map('test_direct.ccp4')

  # read back directly
  new_mm=map_manager('test_direct.ccp4')
  assert (not new_mm.is_similar(mm))

  new_mm.shift_origin()
  assert mm.is_similar(new_mm)

  # deep_copy
  new_mm=mm.deep_copy()
  assert new_mm.is_similar(mm)

  # deep_copy a map without shifting origin
  dm = DataManager(['miller_array','real_map', 'phil'])
  dm.set_overwrite(True)
  dm.process_real_map_file(data_ccp4)
  omm = dm.get_real_map()
  omm.show_summary()
  new_omm=omm.deep_copy()
  assert new_omm.is_similar(omm)
  assert (not new_omm.is_similar(mm))

  # customized_copy
  new_mm=mm.customized_copy(map_data=mm.map_data().deep_copy())
  assert new_mm.is_similar(mm)


  # Initialize with parameters
  mm_para=map_manager(
     unit_cell_grid= mm.unit_cell_grid,
     unit_cell_crystal_symmetry= mm.unit_cell_crystal_symmetry(),
     origin_shift_grid_units= mm.origin_shift_grid_units,
     map_data=mm.map_data())
  assert mm_para.is_similar(mm)

  # Adjust origin and gridding:
  mm_read=map_manager(data_ccp4)
  mm_read.shift_origin()
  mm.show_summary()
  mm_read.show_summary()
  mm_read.set_original_origin_and_gridding((10,10,10),gridding=(100,100,100))
  mm_read.show_summary()
  assert (not mm_read.is_similar(mm))
  assert (mm_read.origin_is_zero())

  # Set program name
  mm_read.set_program_name('test program')
  assert mm_read.program_name=='test program'

  # Set limitation
  mm_read.add_limitation('map_is_sharpened')
  assert mm_read.limitations==['map_is_sharpened']

  # Add a label
  mm_read.add_label('TEST LABEL')
  assert mm_read.labels[0]=='TEST LABEL'
  mm_read.write_map('map_with_labels.mrc')
  new_mm=map_manager('map_with_labels.mrc')
  assert 'TEST LABEL' in new_mm.labels
  assert new_mm.is_in_limitations('map_is_sharpened')
  assert new_mm.labels[0].find('test program')>-1

  # Read a map directly
  mm_read=map_manager(data_ccp4)
  mm_read.shift_origin()
  assert mm_read.is_similar(mm)

  # Set log
  import sys
  mm.set_log(sys.stdout)

  # Add map_data
  new_mm=mm_read.customized_copy(map_data=mm.map_data().deep_copy())
  assert new_mm.is_similar(mm)

  # replace data
  new_mm.set_map_data(map_data=mm.map_data().deep_copy())
  assert new_mm.is_similar(mm)

  # Apply a mask to edges of a map
  assert approx_equal(new_mm.map_data().as_1d().min_max_mean().max,
                          mm.map_data().as_1d().min_max_mean().max)
  assert approx_equal( (new_mm.map_data()[0],mm.map_data()[0]),
         (0.0, 0.0))
  new_mm.create_mask_around_edges(soft_mask_radius=3)
  new_mm.soft_mask(soft_mask_radius=3)
  assert approx_equal(new_mm.map_data().as_1d().min_max_mean().max,
                          mm.map_data().as_1d().min_max_mean().max)
  new_mm.apply_mask(set_outside_to_mean_inside=True)
  assert approx_equal( (new_mm.map_data()[0],mm.map_data()[0]),
         (0.0116267086024, 0.0))


  dm.process_real_map_file('test_map_manager.ccp4')
  new_mm=dm.get_real_map('test_map_manager.ccp4')
  new_mm.show_summary()
  assert (not new_mm.is_similar(mm))
  new_mm.shift_origin()
  new_mm.show_summary()
  assert new_mm.is_similar(mm)
  os.remove('test_map_manager.ccp4')

  # Check origin_shifts
  print (new_mm.origin_shift_grid_units)
  print (new_mm.origin_shift_cart())
  assert approx_equal(new_mm.origin_shift_grid_units,(100,100,100))
  assert approx_equal(new_mm.origin_shift_cart(),
       (74.70333099365234, 72.30750274658205, 73.7437515258789))
  # Convert to map coeffs, write out, read back, convert back to map

  map_coeffs = mm.map_as_fourier_coefficients(high_resolution = 3)
  mtz_dataset = map_coeffs.as_mtz_dataset(column_root_label='F')
  mtz_object=mtz_dataset.mtz_object()
  dm.write_miller_array_file(mtz_object, filename="map_coeffs.mtz")
  # Note these Fourier coeffs correspond to working map (not original position)

  array_labels=dm.get_miller_array_labels("map_coeffs.mtz")
  labels=array_labels[0]
  dm.get_reflection_file_server(filenames=["map_coeffs.mtz"],labels=[labels])
  miller_arrays=dm.get_miller_arrays()
  new_map_coeffs=miller_arrays[0]
  map_data_from_map_coeffs=mm.fourier_coefficients_as_map(
      map_coeffs=new_map_coeffs)

  mm_from_map_coeffs=mm.customized_copy(map_data=map_data_from_map_coeffs)
  assert mm_from_map_coeffs.is_similar(mm)

if (__name__ == '__main__'):
  test_01()
  print ("OK")
