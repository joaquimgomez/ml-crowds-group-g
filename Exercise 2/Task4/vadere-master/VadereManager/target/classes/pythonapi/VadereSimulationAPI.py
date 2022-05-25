#
# Generated source file. DO NOT CHANGE!

from .domain import Domain
from . import VadereConstants as tc


class VadereSimulationAPI(Domain):
    def __init__(self):
        Domain.__init__(self, "v_simulation",tc.CMD_GET_V_SIM_VARIABLE, tc.CMD_SET_V_SIM_VARIABLE, 
                                tc.CMD_SUBSCRIBE_V_SIM_VARIABLE, tc.RESPONSE_SUBSCRIBE_V_SIM_VARIABLE, 
                                tc.CMD_SUBSCRIBE_V_SIM_CONTEXT, tc.RESPONSE_SUBSCRIBE_V_SIM_CONTEXT)

    def get_data_processor_value(self, element_id):
        return self._getUniversal(tc.VAR_DATA_PROCESSOR, element_id)

    def get_network_bound(self):
        return self._getUniversal(tc.VAR_NET_BOUNDING_BOX, "")

    def get_time(self):
        return self._getUniversal(tc.VAR_TIME, "")

    def get_time_ms(self):
        return self._getUniversal(tc.VAR_TIME_MS, "")

    def get_sim_ste(self):
        return self._getUniversal(tc.VAR_DELTA_T, "")

    def init_control(self):
        self._setCmd(tc.VAR_EXTERNAL_INPUT_INIT, "", "Error", None)

    def apply_control(self):
        self._setCmd(tc.VAR_EXTERNAL_INPUT, "", "Error", None)

    def set_sim_config(self):
        self._setCmd(tc.VAR_SIM_CONFIG, "", "Error", None)

    def get_sim_config(self):
        return self._getUniversal(tc.VAR_SIM_CONFIG, "")

    def get_hash(self, data):
        return self._getUniversal(tc.VAR_CACHE_HASH, "", data)

    def get_departed_pedestrian_id(self, data):
        return self._getUniversal(tc.VAR_DEPARTED_PEDESTRIAN_IDS, "", data)

    def get_arrived_pedestrian_ids(self, data):
        return self._getUniversal(tc.VAR_ARRIVED_PEDESTRIAN_PEDESTRIAN_IDS, "", data)

    def get_position_conversion(self, data):
        return self._getUniversal(tc.VAR_POSITION_CONVERSION, "", data)

    def get_coordinate_reference(self, data):
        return self._getUniversal(tc.VAR_COORD_REF, "", data)

    def get_output_dir(self, data):
        return self._getUniversal(tc.VAR_OUTPUT_DIR, "", data)

    def get_obstacles(self, data):
        return self._getUniversal(tc.VAR_OBSTACLES, "", data)

