import orca
from urbansim.utils import misc

############################
# small drive network vars #
############################
@orca.column('parcels')
def node_id_small(parcels, netsmall):
    idssmall_parcel = netsmall.get_node_ids(parcels.x, parcels.y)
    return idssmall_parcel


@orca.column('rentals')
def node_id_small(rentals, netsmall):
    idssmall_rentals = netsmall.get_node_ids(
        rentals.longitude, rentals.latitude)
    return idssmall_rentals


@orca.column('buildings')
def node_id_small(parcels, buildings):
    return misc.reindex(parcels.node_id_small, buildings.parcel_id)


@orca.column('units')
def node_id_small(buildings, units):
    return misc.reindex(buildings.node_id_small, units.building_id)


@orca.column('households')
def node_id_small(units, households):
    return misc.reindex(units.node_id_small, households.unit_id)


@orca.column('persons')
def node_id_small(households, persons):
    return misc.reindex(households.node_id_small, persons.household_id)


@orca.column('jobs')
def node_id_small(buildings, jobs):
    return misc.reindex(buildings.node_id_small, jobs.building_id)


###########################
#### walk network vars ####
###########################
@orca.column('parcels')
def node_id_walk(parcels, netwalk):
    idswalk_parcel = netwalk.get_node_ids(parcels.x, parcels.y)
    return idswalk_parcel


@orca.column('rentals')
def node_id_walk(rentals, netwalk):
    idswalk_rentals = netwalk.get_node_ids(rentals.longitude, rentals.latitude)
    return idswalk_rentals


@orca.column('buildings')
def node_id_walk(parcels, buildings):
    return misc.reindex(parcels.node_id_walk, buildings.parcel_id)


@orca.column('units')
def node_id_walk(buildings, units):
    return misc.reindex(buildings.node_id_walk, units.building_id)


@orca.column('households')
def node_id_walk(units, households):
    return misc.reindex(units.node_id_walk, households.unit_id)


@orca.column('persons')
def node_id_walk(households, persons):
    return misc.reindex(households.node_id_walk, persons.household_id)


@orca.column('jobs')
def node_id_walk(buildings, jobs):
    return misc.reindex(buildings.node_id_walk, jobs.building_id)


###########################
#### beam network vars ####
###########################
# @orca.column('parcels')
# def node_id_beam(parcels, netbeam):
#     idsbeam_parcel = netbeam.get_node_ids(parcels.x, parcels.y)
#     return idsbeam_parcel


# @orca.column('rentals')
# def node_id_beam(rentals, netbeam):
#     idsbeam_rentals = netbeam.get_node_ids(
#         rentals.longitude, rentals.latitude)
#     return idsbeam_rentals


# @orca.column('buildings')
# def node_id_beam(parcels, buildings):
#     return misc.reindex(parcels.node_id_beam, buildings.parcel_id)


# @orca.column('jobs')
# def node_id_beam(buildings, jobs):
#     return misc.reindex(buildings.node_id_beam, jobs.building_id)
