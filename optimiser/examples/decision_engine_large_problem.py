import sys

sys.path.append("../src/")

from decision_engine import SupplierSelectionModel
from utils import generate_supplier_selector_variables, compute_reduced_price


(
    price,
    demand,
    capacity,
    share,
    supplier_transfer_limit,
    min_units,
    trust,
) = generate_supplier_selector_variables(
    n_suppliers=30, n_parts=1000, n_years=10, print_data=False, seed=1
)

# scenario = SupplierSelectionModel(
#     price,
#     demand,
#     capacity=capacity,
#     supplier_transfer_limit=supplier_transfer_limit,
#     share=share,
#     global_transfer_limit=10,
#     minimum_units=min_units,
#     trust=trust,
# )

scenario = SupplierSelectionModel(
    price,
    demand,
    capacity=capacity
)

scenario.minimise_cost()
