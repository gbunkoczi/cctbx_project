from __future__ import division
import iotbx.phil
from cctbx import crystal
from mmtbx.refinement import rigid_body
from cctbx.array_family import flex
from libtbx.utils import Sorry
import random
import scitbx.matrix
import sys
import scitbx.rigid_body
from libtbx import group_args
import mmtbx.monomer_library.server
import mmtbx.utils

mon_lib_srv = mmtbx.monomer_library.server.server()

master_params_str = """\
modify
  .short_caption = Modify starting model
  .style = menu_item scrolled auto_align
{
remove = None
  .type = atom_selection
  .help = Selection for the atoms to be removed
  .short_caption=Remove atom selection
  .input_size=400
  .style = bold noauto
keep = None
  .type = atom_selection
  .help = Select atoms to keep
  .short_caption=Keep only atom selection
  .input_size=400
  .style = bold noauto
put_into_box_with_buffer = None
  .type = float
  .help = Move molecule into center of box.
selection = None
  .type = atom_selection
  .help = Selection for atoms to be modified
  .short_caption = Modify atom selection
  .input_size=400
  .style = bold noauto
adp
  .help = Scope of options to modify ADP of selected atoms
  .multiple = True
  .short_caption=Modify ADPs
  .style = auto_align menu_item parent_submenu:model_modifications noauto
{
  atom_selection = None
    .type = atom_selection
    .help = Selection for atoms to be modified. \\
            Overrides parent-level selection.
    .short_caption = Modify ADPs for selection
    .input_size=400
    .style  = bold
  randomize = False
    .type = bool
    .help = Randomize ADP within a certain range
    .short_caption=Randomize ADPs
  set_b_iso = None
    .type = float
    .help = Set ADP of atoms to set_b_iso
    .short_caption=Set isotropic B to
    .input_size = 64
  convert_to_isotropic = False
    .type = bool
    .help = Convert atoms to isotropic
  convert_to_anisotropic = False
    .type = bool
    .help = Convert atoms to anisotropic
  shift_b_iso = None
    .type = float
    .help = Add shift_b_iso value to ADP
    .short_caption=Increase B_iso by
  scale_adp = None
    .type = float
    .help = Multiply ADP by scale_adp
    .short_caption=ADP scale factor
}
sites
  .help = Scope of options to modify coordinates of selected atoms
  .multiple = True
  .short_caption=Modify coordinates
  .style = auto_align noauto menu_item parent_submenu:model_modifications
{
  atom_selection = None
    .type = atom_selection
    .help = Selection for atoms to be modified. \\
            Overrides parent-level selection.
    .input_size=400
    .short_caption = Modify sites for selection
    .style = bold
  shake = None
    .type = float
    .help = Randomize coordinates with mean error value equal to shake
    .short_caption = Randomize coordinates (mean value)
  switch_rotamers = max_distant min_distant exact_match fix_outliers
    .type=choice(multi=False)
  translate = 0 0 0
    .type = floats(size=3)
    .optional = False
    .help = Translational shift (x,y,z)
  rotate = 0 0 0
    .type = floats(size=3)
    .optional = False
    .help = Rotational shift (x,y,z)
  euler_angle_convention = *xyz zyz
    .type = choice
    .help = Euler angles convention to be used for rotation
}
occupancies
  .help = Scope of options to modify occupancies of selected atoms
  .multiple = True
  .short_caption=Modify occupancies
  .style  = noauto menu_item parent_submenu:model_modifications
{
  atom_selection = None
    .type = atom_selection
    .help = Selection for atoms to be modified. \\
            Overrides parent-level selection.
    .input_size=400
    .short_caption = Modify sites for selection
    .style = bold
  randomize = False
    .type = bool
    .help = Randomize occupancies within a certain range
    .short_caption = Randomize occupancies
  set = None
    .type = float
    .help = Set all or selected occupancies to given value
    .short_caption=Set occupancies to
    .input_size = 64
}
rotate_about_axis
  .style = box auto_align
{
  axis = None
    .type = str
  angle = None
    .type = float
  atom_selection = None
    .type = str
}
change_of_basis = None
  .type = str
  .short_caption = Change of basis operator
  .help = Apply change-of-basis operator (e.g. reindexing operator) to \
    the coordinates and symmetry.  Example: 'a,c,b'.
renumber_residues = False
  .type = bool
  .help = Re-number residues
increment_resseq = None
  .type = int
  .help = Increment residue number
  .short_caption = Increment residue numbers by
truncate_to_polyala = False
  .type = bool
  .help = Truncate a model to poly-Ala.
  .short_caption = Truncate to poly-Ala
  .style = noauto
truncate_to_polygly  = False
  .type = bool
  .help = Truncate a model to poly-Gly.
  .short_caption = Truncate to poly-Gly
  .style = noauto
remove_alt_confs = False
  .type = bool
  .help = Deletes atoms whose altloc identifier is not blank or 'A', and \
    resets the occupancies of the remaining atoms to 1.0.
  .short_caption = Remove alternate conformers
  .style = noauto
always_keep_one_conformer = False
  .type = bool
  .help = Modifies behavior of remove_alt_confs so that residues with no \
    conformer labeled blank or A are not deleted.  Silent if remove_alt_confs \
    is False.
set_chemical_element_simple_if_necessary = None
  .type = bool
  .short_caption = Guess element field if necessary
  .help = Make a simple guess about what the chemical element is (based on \
          atom name and the way how it is formatted) and write it into output file.
set_seg_id_to_chain_id = False
  .type = bool
  .short_caption = Set segID to chain ID
  .help = Sets the segID field to the chain ID (padded with spaces).
  .style = noauto
clear_seg_id = False
  .type = bool
  .short_caption = Clear segID field
  .help = Erases the segID field.
  .style = noauto
convert_semet_to_met = False
  .type = bool
  .short_caption = Convert SeMet residues to Met
  .style = noauto
convert_met_to_semet = False
  .type = bool
  .short_caption = Convert Met residues to SeMet
  .style = noauto
rename_chain_id
  .help = Rename chains
  .short_caption = Rename chain ID
  .style = box
{
  old_id = None
    .type = str
    .input_size = 50
    .short_caption = Old ID
  new_id = None
    .type = str
    .input_size = 50
    .short_caption = New ID
}
set_charge
  .short_caption = Set atomic charge
  .style = box auto_align
{
  charge_selection = None
    .type = atom_selection
    .short_caption = Atom selection
  charge = None
    .type = int(value_max=7,value_min=-3)
}
remove_fraction = None
  .short_caption = Remove atoms randomly (fraction)
  .type = float
random_seed = None
  .type = int
  .help = Random seed
move_waters_last = False
  .type = bool
  .short_caption = Move waters to end of model
  .help = Transfer waters to the end of the model.  Addresses some \
    limitations of water picking in phenix.refine.
}
"""

def master_params():
  return iotbx.phil.parse(master_params_str, process_includes=False)

class modify(object):
  def __init__(self, xray_structure, params, pdb_hierarchy, log = None):
    self.log = log
    self.pdb_hierarchy = pdb_hierarchy
    self.crystal_symmetry = xray_structure.crystal_symmetry()
    if(self.log is None): self.log = sys.stdout
    self.xray_structure = xray_structure
    self.params = params
    asc = self.pdb_hierarchy.atom_selection_cache(
        special_position_settings=crystal.special_position_settings(
            crystal_symmetry = self.crystal_symmetry))
    if(self.params.random_seed is not None):
      random.seed(self.params.random_seed)
      flex.set_random_seed(self.params.random_seed)
    self.top_selection = flex.smart_selection(
        flags=flex.bool(xray_structure.scatterers().size(), True))
    if(self.params.selection is not None):
      self.top_selection = flex.smart_selection(
        flags=asc.selection(self.params.selection))
    self._rotate_about_axis()
    self._process_adp()
    self._process_sites()
    self._process_occupancies()
    self._put_in_box()
    self._change_of_basis()
    # Up to this point we are done with self.xray_structure
    self.pdb_hierarchy.adopt_xray_structure(self.xray_structure)
    # Now only manipulations that use self.pdb_hierarchy are done
### segID manipulations
    if (params.set_seg_id_to_chain_id) :
      if (params.clear_seg_id) :
        raise Sorry("Parameter conflict - set_seg_id_to_chain_id=True and "+
          "clear_seg_id=True.  Please choose only one of these options.")
      for atom in pdb_hierarchy.atoms() :
        labels = atom.fetch_labels()
        atom.segid = "%-4s" % labels.chain_id
    elif (params.clear_seg_id) :
      for atom in pdb_hierarchy.atoms() :
        atom.segid = "    "
    if(self.params.set_chemical_element_simple_if_necessary or
       self.params.rename_chain_id.old_id or
       self.params.renumber_residues or self.params.increment_resseq or
       self.params.convert_semet_to_met or
       self.params.convert_met_to_semet or
       self.params.set_charge.charge or
       self.params.truncate_to_polyala or
       self.params.truncate_to_polygly or
       self.params.remove_alt_confs or
       self.params.move_waters_last or
       self.params.remove_fraction or
       self.params.keep or
       self.params.remove):
      del self.xray_structure # it is invalide below this point
      self._set_chemical_element_simple_if_necessary()
      self._rename_chain_id()
      self._renumber_residues()
      self._convert_semet_to_met()
      self._convert_met_to_semet()
      self._set_atomic_charge()
      self._truncate_to_poly_ala()
      self._truncate_to_poly_gly()
      self._remove_alt_confs()
      self._move_waters()
      self._remove_atoms()
      self._apply_keep_remove()

  def _apply_keep_remove(self):
    cn = [self.params.remove, self.params.keep].count(None)
    if(not cn in [1,2]):
      raise Sorry("'keep' and 'remove' keywords cannot be used simultaneously.")
    s1 = self.pdb_hierarchy.atoms_size()
    if(self.params.remove is not None):
      asc = self.pdb_hierarchy.atom_selection_cache(
        special_position_settings=crystal.special_position_settings(
            crystal_symmetry = self.crystal_symmetry))
      sel = ~asc.selection(self.params.remove)
      self.pdb_hierarchy = self.pdb_hierarchy.select(sel)
      s2 = self.pdb_hierarchy.atoms_size()
      print >> self.log, "Size before:", s1, "size after:", s2
    if(self.params.keep is not None):
      asc = self.pdb_hierarchy.atom_selection_cache(
        special_position_settings=crystal.special_position_settings(
            crystal_symmetry = self.crystal_symmetry))
      sel = asc.selection(self.params.keep)
      self.pdb_hierarchy = self.pdb_hierarchy.select(sel)
      s2 = self.pdb_hierarchy.atoms_size()
      print >> self.log, "Size before:", s1, "size after:", s2

  def _change_of_basis(self):
    if(self.params.change_of_basis is not None):
      print >> self.log, "Applying change-of-basis operator '%s'" % \
        self.params.change_of_basis
      from cctbx import sgtbx
      cb_op = sgtbx.change_of_basis_op(self.params.change_of_basis)
      self.xray_structure = self.xray_structure.change_basis(cb_op)
      self.pdb_hierarchy.atoms().set_xyz(self.xray_structure.sites_cart())
      print >> self.log, "New symmetry:"
      self.xray_structure.crystal_symmetry().show_summary(f=self.log, prefix="  ")
      self.crystal_symmetry = self.xray_structure.crystal_symmetry()

  def _move_waters(self):
    if(self.params.move_waters_last):
      print >> self.log, "Moving waters to end of model"
      if (len(self.pdb_hierarchy.models()) > 1) :
        raise Sorry("Rearranging water molecules is not supported for "+
          "multi-MODEL structures.")
      sel_cache = self.pdb_hierarchy.atom_selection_cache(
        special_position_settings=crystal.special_position_settings(
            crystal_symmetry = self.crystal_symmetry))
      water_sel = sel_cache.selection("resname HOH or resname WAT") # BAD XXX
      n_waters = water_sel.count(True)
      if (n_waters == 0) :
        print >> self.log, "No waters found, skipping"
      else :
        print >> self.log, "%d atoms will be moved." % n_waters
        hierarchy_water = self.pdb_hierarchy.select(water_sel)
        hierarchy_non_water = self.pdb_hierarchy.select(~water_sel)
        for chain in hierarchy_water.only_model().chains() :
          hierarchy_non_water.only_model().append_chain(chain.detached_copy())
        self.pdb_hierarchy = hierarchy_non_water # does this work?

  def _remove_alt_confs(self):
    if(self.params.remove_alt_confs):
      print >> self.log, "Remove altlocs"
      always_keep_one_conformer = self.params.always_keep_one_conformer
      self.pdb_hierarchy.remove_alt_confs(
        always_keep_one_conformer = self.params.always_keep_one_conformer)

  def _truncate_to_poly_gly(self):
    if(self.params.truncate_to_polygly):
      print >> self.log, "Truncate to poly-gly"
      self.pdb_hierarchy.truncate_to_poly_gly()

  def _truncate_to_poly_ala(self):
    if(self.params.truncate_to_polyala):
      print >> self.log, "Truncate to poly-ala"
      self.pdb_hierarchy.truncate_to_poly_ala()

  def _set_atomic_charge(self):
    if(self.params.set_charge.charge_selection is not None):
      print >> self.log, "Setting atomic charge"
      selection = self.params.set_charge.charge_selection
      charge    = self.params.set_charge.charge
      sel_cache = self.pdb_hierarchy.atom_selection_cache(
        special_position_settings=crystal.special_position_settings(
            crystal_symmetry = self.crystal_symmetry))
      isel = sel_cache.selection(selection).iselection()
      self.pdb_hierarchy.set_atomic_charge(iselection=isel, charge=charge)

  def _convert_met_to_semet(self):
    if(self.params.convert_met_to_semet):
      print >> self.log, "Convert MET->MSE"
      self.pdb_hierarchy.convert_met_to_semet()

  def _convert_semet_to_met(self):
    if(self.params.convert_semet_to_met) :
      print >> self.log, "Convert MSE->MET"
      self.pdb_hierarchy.convert_semet_to_met()

  def _renumber_residues(self):
    if((self.params.increment_resseq) or
       (self.params.renumber_residues)):
      print >> self.log, "Re-numbering residues"
      renumber_from  = self.params.increment_resseq
      atom_selection = self.params.selection
      pdb_hierarchy  = self.pdb_hierarchy
      selected_i_seqs = None
      if (atom_selection is not None) :
        sel_cache = pdb_hierarchy.atom_selection_cache(
        special_position_settings=crystal.special_position_settings(
            crystal_symmetry = self.crystal_symmetry))
        selected_i_seqs = sel_cache.selection(atom_selection).iselection()
      for model in pdb_hierarchy.models():
        for chain in model.chains():
          if (selected_i_seqs is not None) :
            chain_i_seqs = chain.atoms().extract_i_seq()
            intersection = selected_i_seqs.intersection(chain_i_seqs)
            if (len(intersection) == 0) :
              continue
            elif (len(intersection) != len(chain_i_seqs)) :
              print >> self.log, "Warning: chain '%s' is only partially selected (%d out of %d) - will not renumber." % (chain.id, len(intersection), len(chain_i_seqs))
              continue
          if (renumber_from is None) :
            counter = 1
            for rg in chain.residue_groups():
              rg.resseq=counter
              counter += 1
          else :
            for rg in chain.residue_groups() :
              resseq = rg.resseq_as_int()
              resseq += renumber_from
              rg.resseq = "%4d" % resseq

  def _rename_chain_id(self):
    if([self.params.rename_chain_id.old_id,
       self.params.rename_chain_id.new_id].count(None)==0):
      print >> self.log, "Rename chain id"
      print >> self.log, "old_id= '%s'"%self.params.rename_chain_id.old_id
      print >> self.log, "new_id= '%s'"%self.params.rename_chain_id.new_id
      self.pdb_hierarchy.rename_chain_id(
        old_id = self.params.rename_chain_id.old_id,
        new_id = self.params.rename_chain_id.new_id)

  def _set_chemical_element_simple_if_necessary(self):
    if(self.params.set_chemical_element_simple_if_necessary):
      print >> self.log, "Set chemical element"
      self.pdb_hierarchy.atoms().set_chemical_element_simple_if_necessary()

  def _remove_atoms(self):
    if(self.params.remove_fraction is not None):
      self.pdb_hierarchy = \
        self.pdb_hierarchy.remove_atoms(fraction=self.params.remove_fraction)

  def _put_in_box(self):
    if(self.params.put_into_box_with_buffer is not None):
      result = \
        self.xray_structure.orthorhombic_unit_cell_around_centered_scatterers(
          buffer_size = self.params.put_into_box_with_buffer)
      self.xray_structure.replace_scatterers(result.scatterers())

  def _print_action(self, text, selection):
    print >> self.log, "%s: selected atoms: %s" % (
      text, selection.format_summary())

  def _process_adp(self):
    for adp in self.params.adp:
      if (adp.atom_selection is None):
        selection = self.top_selection
      else:
        asc = self.pdb_hierarchy.atom_selection_cache(
        special_position_settings=crystal.special_position_settings(
            crystal_symmetry = self.crystal_symmetry))
        sel = asc.selection(adp.atom_selection)
        selection = flex.smart_selection(flags=sel)
      if (adp.convert_to_isotropic):
        self._convert_to_isotropic(selection=selection)
      if (adp.convert_to_anisotropic):
        self._convert_to_anisotropic(selection=selection)
      self._set_b_iso(selection=selection, b_iso=adp.set_b_iso)
      self._scale_adp(selection=selection, factor=adp.scale_adp)
      self._shift_b_iso(selection=selection, shift=adp.shift_b_iso)
      if (adp.randomize):
        self._randomize_adp(selection=selection)

  def _convert_to_isotropic(self, selection):
    self._print_action(
      text = "Converting to isotropic ADP",
      selection = selection)
    self.xray_structure.convert_to_isotropic(selection=selection.indices)

  def _convert_to_anisotropic(self, selection):
    self._print_action(
      text = "Converting to anisotropic ADP",
      selection = selection)
    self.xray_structure.convert_to_anisotropic(selection=selection.flags)

  def _set_b_iso(self, selection, b_iso):
    if (b_iso is not None):
      self._print_action(
        text = "Setting all isotropic ADP = %.3f" % b_iso,
        selection = selection)
      self.xray_structure.set_b_iso(value=b_iso, selection=selection.flags)

  def _scale_adp(self, selection, factor):
    if (factor is not None):
      self._print_action(
        text = "Multiplying all ADP with factor = %.6g" % factor,
        selection = selection)
      self.xray_structure.scale_adp(factor=factor, selection=selection.flags)

  def _shift_b_iso(self, selection, shift):
    if (shift is not None):
      self._print_action(
        text = "Adding shift = %.2f to all ADP" % shift,
        selection = selection)
      self.xray_structure.shift_us(b_shift=shift, selection=selection.indices)

  def _randomize_adp(self, selection):
    self._print_action(
      text = "Randomizing ADP",
      selection = selection)
    self.xray_structure.shake_adp(selection=selection.flags)

  def _process_sites(self):
    for sites in self.params.sites:
      if (sites.atom_selection is None):
        selection = self.top_selection
      else:
        asc = self.pdb_hierarchy.atom_selection_cache(
        special_position_settings=crystal.special_position_settings(
            crystal_symmetry = self.crystal_symmetry))
        sel = asc.selection(sites.atom_selection)
        selection = flex.smart_selection(flags=sel)
      self._shake_sites(selection=selection, rms_difference=sites.shake)
      self._switch_rotamers(selection=selection, mode=sites.switch_rotamers)
      self._rb_shift(
        selection=selection,
        translate=sites.translate,
        rotate=sites.rotate,
        euler_angle_convention=sites.euler_angle_convention)

  def _switch_rotamers(self, selection, mode):
    if(mode is None): return
    self._print_action(
      text = "Switching rotamers; mode = %s"%mode,
      selection = selection)
    self.pdb_hierarchy.atoms().set_xyz(self.xray_structure.sites_cart())
    self.pdb_hierarchy = mmtbx.utils.switch_rotamers(
      pdb_hierarchy=self.pdb_hierarchy,
      mode=mode,
      selection=selection.flags)
    self.xray_structure.set_sites_cart(
      sites_cart = self.pdb_hierarchy.atoms().extract_xyz())

  def _shake_sites(self, selection, rms_difference):
    if (rms_difference is not None):
      self._print_action(
        text = "Shaking sites (RMS = %.3f)" % rms_difference,
        selection = selection)
      self.xray_structure.shake_sites_in_place(
        rms_difference=rms_difference,
        selection=selection.flags)

  def _rb_shift(self, selection, translate, rotate, euler_angle_convention):
    trans = [float(i) for i in translate]
    rot   = [float(i) for i in rotate]
    if(len(trans) != 3): raise Sorry("Wrong value: translate= " + translate)
    if(len(rot) != 3): raise Sorry("Wrong value: translate= " + rotate)
    if (   trans[0] != 0 or trans[1] != 0 or trans[2] != 0
        or rot[0] != 0 or rot[1] != 0 or rot[2] != 0):
      self._print_action(
        text = "Rigid body shift",
        selection = selection)
      if (euler_angle_convention == "zyz"):
        rot_obj = scitbx.rigid_body.rb_mat_zyz(
          phi = rot[0],
          psi = rot[1],
          the = rot[2])
      else:
        rot_obj = scitbx.rigid_body.rb_mat_xyz(
          phi = rot[0],
          psi = rot[1],
          the = rot[2])
      self.xray_structure.apply_rigid_body_shift(
        rot       = rot_obj.rot_mat().as_mat3(),
        trans     = trans,
        selection = selection.indices)

  def _process_occupancies(self):
    def check_if_already_modified() :
      if(self.top_selection): return
      if (self._occupancies_modified):
        raise Sorry("Can't modify occupancies (already modified).")
      else:
        self._occupancies_modified = True
    for occ in self.params.occupancies:
      if(occ.atom_selection is None):
        selection = self.top_selection
      else:
        asc = self.pdb_hierarchy.atom_selection_cache(
        special_position_settings=crystal.special_position_settings(
            crystal_symmetry = self.crystal_symmetry))
        sel = asc.selection(occ.atom_selection)
        selection = flex.smart_selection(flags=sel)
      if(occ.randomize):
        self._print_action(
          text = "Randomizing occupancies",
          selection = selection)
        check_if_already_modified()
        self.xray_structure.shake_occupancies(selection=selection.flags)
      if(occ.set is not None):
        self._print_action(
          text = "Setting occupancies to: %8.3f"%occ.set, selection = selection)
        check_if_already_modified()
        self.xray_structure.set_occupancies(
            value = occ.set,
            selection = selection.flags)

  def _rotate_about_axis(self):
    raap = self.params.rotate_about_axis
    sites_cart = self.xray_structure.sites_cart()
    if([raap.axis, raap.atom_selection, raap.angle].count(None)==0):
      axis = []
      try:
        for a in raap.axis.split():
          axis.append(float(a))
      except Exception:
        sel = utils.get_atom_selections(
          iselection=False,
          all_chain_proxies=self.all_chain_proxies,
          selection_strings=raap.axis,
          xray_structure=self.xray_structure)[0]
        axis = [i for i in sites_cart.select(sel).as_double()]
      if(len(axis)!=6):
        raise Sorry("Bad selection rotate_about_axis.axis: %s"%str(raap.axis))
      p1 = scitbx.matrix.col(axis[:3])
      p2 = scitbx.matrix.col(axis[3:])
      raa = p1.rt_for_rotation_around_axis_through(
        point=p2, angle=raap.angle, deg=True)
      #
      sel = utils.get_atom_selections(
          iselection=False,
          all_chain_proxies=self.all_chain_proxies,
          selection_strings=raap.atom_selection,
          xray_structure=self.xray_structure)[0]
      if(sel.count(True)==0):
        raise Sorry(
          "Empty selection rotate_about_axis.selection: %s"%str(raap.atom_selection))
      sites_cart_rotated = raa * sites_cart.select(sel)
      self.xray_structure.set_sites_cart(
        sites_cart.set_selected(sel, sites_cart_rotated))

  def get_results(self):
    return group_args(
      pdb_hierarchy    = self.pdb_hierarchy,
      crystal_symmetry = self.crystal_symmetry)
