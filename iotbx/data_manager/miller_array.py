from __future__ import division, print_function
'''
'''

import iotbx.phil

from cctbx import crystal
from iotbx.data_manager import DataManagerBase
from iotbx.reflection_file_utils import reflection_file_server
from libtbx.str_utils import wordwrap
from libtbx.utils import Sorry

# =============================================================================
# optional PHIL scope for specifying miller_array usage
miller_array_phil_str = '''
data
  .multiple = True
{
  file_name = None
    .type = path
  type = *x_ray neutron electron
    .type = choice(multi=False)
  labels = None
    .type = str
}
'''

def get_reflection_file_server(data_manager, params, datatype='x_ray'):
  '''
  Convenience function for getting a reflection file server based on a selection
  of Miller arrays from the iotbx.data_manager.miller_array.miller_array_phil_str
  PHIL scope

  :params data_manager: DataManager with processed files
  :type data_manager: iotbx.data_manager.DataManager object
  :params params: PHIL extract with set parameters
  :type params: libtbx.phil.scope_extract object
  :params datatype: matches type property in miller_array_phil_str
  :type datatype: str
  :rtype: iotbx.reflection_file_utils.reflection_file_server object or None

  The function returns None if there are no files that match datatype.
  '''

  filenames = list()
  labels = list()

  # find files
  if (hasattr(params, 'data')):
    try:
      for scope in params.data:
        if (scope.type == datatype):
          filenames.append(scope.file_name)
          labels.append(scope.labels)
    except (TypeError, AttributeError):
      raise Sorry(wordwrap('The "data" scope is not in the expected format. See iotbx.data_manager.miller_array.miller_array_phil_str for the expected format.'))

  # get file server
  rfs = None
  if (len(filenames) > 0):
    rfs = data_manager.get_reflection_file_server(filenames=filenames,
                                                  labels=labels)
  return rfs

# =============================================================================
class MillerArrayDataManager(DataManagerBase):

  datatype = 'miller_array'
  miller_array_child_datatypes = list()                     # track children

  # ---------------------------------------------------------------------------
  # Miller arrays

  def add_miller_array_phil_str(self):
    '''
    Add custom PHIL and storage for labels
    '''
    return self._add_miller_array_phil_str(MillerArrayDataManager.datatype)

  def export_miller_array_phil_extract(self):
    '''
    Export custom PHIL extract
    '''
    return self._export_miller_array_phil_extract(
      MillerArrayDataManager.datatype)

  def load_miller_array_phil_extract(self, phil_extract):
    '''
    Load custom PHIL extract
    '''
    self._load_miller_array_phil_extract(MillerArrayDataManager.datatype,
                                         phil_extract)

  def add_miller_array(self, filename, data):
    self._add(MillerArrayDataManager.datatype, filename, data)
    self._filter_miller_array_child_datatypes(filename)

  def set_default_miller_array(self, filename):
    return self._set_default(MillerArrayDataManager.datatype, filename)

  def get_miller_array(self, filename=None):
    '''
    Returns the main file object
    '''
    return self._get(MillerArrayDataManager.datatype, filename)

  def get_miller_array_labels(self, filename=None):
    '''
    Returns a list of array labels
    '''
    return self._get_array_labels(MillerArrayDataManager.datatype, filename)

  def get_miller_arrays(self, labels=None, filename=None):
    '''
    Returns a list of arrays
    '''
    return self._get_arrays(MillerArrayDataManager.datatype, labels=labels,
                            filename=filename)

  def get_miller_array_names(self):
    return self._get_names(MillerArrayDataManager.datatype)

  def get_default_miller_array_name(self):
    return self._get_default_name(MillerArrayDataManager.datatype)

  def remove_miller_array(self, filename):
    return self._remove(MillerArrayDataManager.datatype, filename)

  def has_miller_arrays(self, expected_n=1, exact_count=False, raise_sorry=False):
    return self._has_data(MillerArrayDataManager.datatype, expected_n=expected_n,
                          exact_count=exact_count, raise_sorry=raise_sorry)

  def process_miller_array_file(self, filename):
    self._process_file(MillerArrayDataManager.datatype, filename)
    self._filter_miller_array_child_datatypes(filename)

  def filter_miller_array_arrays(self, filename):
    '''
    Populate data structures with all arrays
    '''
    if (filename not in self._miller_array_arrays.keys()):
      self._miller_array_arrays[filename] = dict()
    miller_arrays = self.get_miller_array(filename).as_miller_arrays()
    labels = list()
    for array in miller_arrays:
      label = array.info().label_string()
      labels.append(label)
      self._miller_array_arrays[filename][label] = array
    self._miller_array_labels[filename] = labels

  def write_miller_array_file(self, filename, miller_arrays, overwrite=False):
    raise NotImplementedError

  def get_reflection_file_server(self, filenames=None, labels=None,
                                 crystal_symmetry=None, force_symmetry=None):
    '''
    Return the file server for a single miller_array file or mulitple files

    :param filenames:         list of filenames or None
    :param labels:            list of lists of labels or None
    :param crystal_symmetry:  cctbx.crystal.symmetry object or None
    :param force_symmetry:    bool or None

    The order in filenames and labels should match, e.g. labels[0] should be the
    labels for filenames[0]. The lengths of filenames and labels should be equal
    as well. If all the labels in a file are to be added, set the labels entry
    to None, e.g. labels[0] = None.
    '''

    # use default miller_array file if no filenames provided
    if (filenames is None):
      default_filename = self._check_miller_array_default_filename(
        'miller_array')
      filenames = [default_filename]

    # set labels
    if (labels is None):
      labels = [None for filename in filenames]

    assert(len(filenames) == len(labels))

    # force crystal symmetry if a crystal symmetry is provided
    if ((crystal_symmetry is not None) and
        (force_symmetry is None)):
      force_symmetry = True
    if (force_symmetry is None):
      force_symmetry = False

    #  determine crystal symmetry from file list, if not provided
    if (crystal_symmetry is None):
      try:
        from_reflection_files = list()
        for filename, file_labels in zip(filenames, labels):
          miller_arrays = self.get_miller_arrays(filename=filename)
          for miller_array in miller_arrays:
            if ((file_labels is None) or
                (miller_array.info().label_string() in file_labels)):
              from_reflection_files.append(miller_array.crystal_symmetry())
        crystal_symmetry = crystal.select_crystal_symmetry(
          from_reflection_files=from_reflection_files)
      except Exception:
        raise Sorry('A unit cell and space group could not be determined from the "filenames" argument. Please provide a list of filenames.')

    # crystal_symmetry and force_symmetry should be set by now
    miller_arrays = list()
    for filename, file_labels in zip(filenames, labels):
      file_arrays = self.get_miller_array(filename=filename).\
        as_miller_arrays(crystal_symmetry=crystal_symmetry,
                         force_symmetry=force_symmetry)
      for miller_array in file_arrays:
        if ((file_labels is None) or
            (miller_array.info().label_string() in file_labels)):
          miller_arrays.append(miller_array)
    file_server = reflection_file_server(
      crystal_symmetry=crystal_symmetry,
      force_symmetry=force_symmetry,
      miller_arrays=miller_arrays)
    return file_server

  # -----------------------------------------------------------------------------
  # base functions for miller_array datatypes
  def _add_miller_array_phil_str(self, datatype):

    # set up storage
    # self._miller_array_labels = dict()      # [filename] = label list
    # self._miller_array_arrays = dict()      # [filename] = array dict
    setattr(self, '_%s_labels' % datatype, dict())
    setattr(self, '_%s_arrays' % datatype, dict())

    # custom PHIL section
    custom_phil_str = '%s\n.multiple = True\n{\n' % datatype
    custom_phil_str += 'file = None\n'
    custom_phil_str += '.type = path\n'

    # property for wx GUI (will be removed)
    custom_phil_str += '.style = file_type:hkl input_file\n'

    custom_phil_str += 'labels = None\n'
    custom_phil_str += '.type = str\n.multiple = True\n'
    custom_phil_str += '}\n'

    # custom PHIL scope
    setattr(self, '_custom_%s_phil' % datatype,
            iotbx.phil.parse(custom_phil_str))

    # add to child datatypes
    MillerArrayDataManager.miller_array_child_datatypes.append(datatype)

    return custom_phil_str

  def _export_miller_array_phil_extract(self, datatype):
    extract = list()
    filenames = getattr(self, 'get_%s_names' % datatype)()
    for filename in filenames:
      item_extract = getattr(self, '_custom_%s_phil' % datatype).extract()
      item_extract = getattr(item_extract, '%s' % datatype)[0]
      item_extract.file = filename
      item_extract.labels = self._get_array_labels(datatype, filename=filename)
      extract.append(item_extract)
    return extract

  def _load_miller_array_phil_extract(self, datatype, phil_extract):
    extract = phil_extract.data_manager
    extract = getattr(extract, '%s' % datatype)
    for item_extract in extract:
      if ( (not hasattr(item_extract, 'file')) or
           (not hasattr(item_extract, 'labels')) ):
        raise Sorry('This PHIL is not properly defined for the %s datatype.\n There should be a parameter for the filename ("file") and labels ("labels").\n')

      # process file
      getattr(self, 'process_%s_file' % datatype)(item_extract.file)
      # update labels
      getattr(self, '_%s_labels' % datatype)[item_extract.file] = \
        item_extract.labels

  def _filter_miller_array_child_datatypes(self, filename):
    # filter arrays (e.g self.filter_map_coefficients_arrays)
    for datatype in MillerArrayDataManager.miller_array_child_datatypes:
      function_name = 'filter_%s_arrays' % datatype
      if (hasattr(self, function_name)):
        getattr(self, function_name)(filename)

  def _check_miller_array_default_filename(self, datatype, filename=None):
    '''
    Helper function for handling default filenames
    '''
    if (filename is None):
      filename = getattr(self, 'get_default_%s_name' % datatype)()
      if (filename is None):
        raise Sorry('There is no default filename for %s.' % datatype)
    return filename

  def _check_miller_array_storage_dict(self, datatype, storage_dict, filename):
    '''
    Helper function for checking filename and datatypes
    '''
    if (filename not in storage_dict.keys()):
      self.process_miller_array_file(filename)
      if (filename not in storage_dict.keys()):
        raise Sorry('There are no known %s arrays in %s' % (datatype, filename))

  def _get_array_labels(self, datatype, filename=None):
    filename = self._check_miller_array_default_filename(datatype, filename)
    storage_dict = getattr(self, '_%s_labels' % datatype)
    self._check_miller_array_storage_dict(datatype, storage_dict, filename)
    labels = storage_dict[filename]

    return labels

  def _get_arrays(self, datatype, filename=None, labels=None):
    filename = self._check_miller_array_default_filename(datatype, filename)
    if (filename not in getattr(self, 'get_%s_names' % datatype)()):
      self.process_miller_array_file(filename)
    if (labels is None):
      labels = self._get_array_labels(datatype, filename=filename)
    else:
      if (not isinstance(labels, list)):
        raise Sorry('The labels argument should be a list of labels')

    storage_dict = getattr(self, '_%s_arrays' % datatype)
    self._check_miller_array_storage_dict(datatype, storage_dict, filename)
    arrays = list()
    for label in labels:
      arrays.append(self._get_array_by_label(datatype, filename, label))
    return arrays

  def _get_array_by_label(self, datatype, filename, label):
    storage_dict = getattr(self, '_%s_arrays' % datatype)
    if (label in storage_dict[filename].keys()):
      return storage_dict[filename][label]
    else:
      raise Sorry('%s does not have any arrays labeled %s' %
                  (filename, label))

  def _child_filter_arrays(self, datatype, filename, known_labels):
    '''
    Populate data structures by checking labels in miller arrays to determine
    child type
    '''
    if (datatype not in MillerArrayDataManager.miller_array_child_datatypes):
      raise Sorry('%s is not a valid child datatype of miller_array.')
    data = self.get_miller_array(filename)
    miller_arrays = data.as_miller_arrays()
    labels = list()
    for array in miller_arrays:
      label = set(array.info().labels)
      common_labels = known_labels.intersection(label)
      if (len(common_labels) > 0):
        labels.append(array.info().label_string())
        datatype_dict = getattr(self, '_%s_arrays' % datatype)
        if (filename not in datatype_dict.keys()):
          datatype_dict[filename] = dict()
        datatype_dict[filename][label] = array

    # if arrays exist, start tracking
    if (len(labels) > 1):
      getattr(self, '_%s_labels' % datatype)[filename] = labels
      self._add(datatype, filename, data)

# =============================================================================
# end
