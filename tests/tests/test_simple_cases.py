from decision_engine_optimiser import (
    MinimalSupplierSelectionModel,
    SupplierSelectionModel,
)
from decision_engine_optimiser.utils import generate_supplier_selector_variables


def test_minimal():
    price = [[60, 605, 95, 75], [50, 615, 98, 60]]
    demand = [300, 20, 150, 80]
    capacity = [2, 3]

    supplier_selection_min_a = MinimalSupplierSelectionModel(price, demand, capacity)
    supplier_selection_min_a.minimise_cost()
    work_details = supplier_selection_min_a.return_volume_value_details()

    assert work_details == [[0, 20, 150, 0], [300, 0, 0, 80]]


def test_share():
    price = [[60, 605, 95, 75], [50, 615, 98, 60]]

    demand = [300, 20, 150, 80]

    capacity = [2, 3]

    share = [[100, 100, 30, 100], [80, 100, 70, 100]]

    supplier_selection_min_b = MinimalSupplierSelectionModel(
        price, demand, capacity, share
    )
    supplier_selection_min_b.minimise_cost(print=True)
    work_details = supplier_selection_min_b.return_volume_value_details()
    assert work_details == [[300, 0, 46, 0], [0, 20, 104, 80]]


def test_transfer_limit():
    price = [
        [[60, 62, 64], [605, 610, 615], [95, 96, 97], [75, 75, 75]],
        [[50, 55, 60], [615, 610, 605], [98, 97, 96], [60, 70, 80]],
    ]

    demand = [[300, 310, 320], [20, 30, 40], [150, 145, 130], [80, 80, 80]]

    capacity = [[4, 4, 4], [3, 3, 3]]

    share = [[100, 100, 30, 100], [80, 100, 70, 100]]

    supplier_transfer_limit = [1, 2]

    supplier_selection_time = SupplierSelectionModel(
        price,
        demand,
        capacity=capacity,
        supplier_transfer_limit=supplier_transfer_limit,
        share=share,
    )
    supplier_selection_time.minimise_cost()
    work_details = supplier_selection_time.return_volume_value_details()
    assert work_details == [
        [[58, 59, 61], [20, 30, 0], [46, 44, 38], [0, 0, 80]],
        [[242, 251, 259], [0, 0, 40], [104, 101, 92], [80, 80, 0]],
    ]


def test_volume_constraint():
    price = [
        [[60, 62, 64], [605, 610, 615], [95, 96, 97], [75, 75, 75]],
        [[50, 55, 60], [615, 610, 605], [98, 97, 96], [60, 70, 80]],
    ]

    demand = [[300, 310, 320], [20, 30, 40], [150, 145, 130], [80, 80, 80]]

    capacity = [[4, 4, 4], [3, 3, 3]]

    share = [[100, 100, 30, 100], [80, 100, 70, 100]]

    supplier_transfer_limit = [1, 2]
    supplier_selection_contract = SupplierSelectionModel(
        price,
        demand,
        capacity=capacity,
        supplier_transfer_limit=supplier_transfer_limit,
        share=share,
    )

    supplier_selection_contract.set_volume_constraint(1, 3, 2, 70)
    supplier_selection_contract.minimise_cost()
    work_details = supplier_selection_contract.return_volume_value_details()
    assert work_details == [
        [[58, 59, 61], [20, 30, 40], [46, 44, 38], [0, 0, 10]],
        [[242, 251, 259], [0, 0, 0], [104, 101, 92], [80, 80, 70]],
    ]


def test_minimum_units():
    price = [
        [[60, 62, 64], [605, 610, 615], [95, 96, 97], [75, 75, 75]],
        [[50, 55, 60], [615, 610, 605], [98, 97, 96], [60, 70, 80]],
    ]

    demand = [[300, 310, 320], [20, 30, 40], [150, 145, 130], [80, 80, 80]]

    capacity = [[4, 4, 4], [3, 3, 3]]

    share = [[100, 100, 30, 100], [80, 100, 70, 100]]

    supplier_transfer_limit = [1, 2]

    min_units = [
        [[100, 100, 100], [5, 5, 5], [20, 25, 30], [15, 15, 15]],
        [[100, 100, 100], [5, 5, 5], [20, 25, 30], [15, 15, 15]],
    ]

    supplier_selection_min_units = SupplierSelectionModel(
        price,
        demand,
        capacity=capacity,
        supplier_transfer_limit=supplier_transfer_limit,
        share=share,
        minimum_units=min_units,
    )

    supplier_selection_min_units.minimise_cost()
    work_details = supplier_selection_min_units.return_volume_value_details()
    assert work_details == [
        [[100, 100, 100], [20, 30, 0], [46, 44, 38], [0, 0, 80]],
        [[200, 210, 220], [0, 0, 40], [104, 101, 92], [80, 80, 0]],
    ]


def test_contractual_requirements():
    """
    Contractual requirement:
        Supplier 1 must provide 70 units of Part 3 in year 2
    """
    price = [
        [[60, 62, 64], [605, 610, 615], [95, 96, 97], [75, 75, 75]],
        [[50, 55, 60], [615, 610, 605], [98, 97, 96], [60, 70, 80]],
    ]

    demand = [[300, 310, 320], [20, 30, 40], [150, 145, 130], [80, 80, 80]]

    capacity = [[4, 4, 4], [3, 3, 3]]

    share = [[100, 100, 30, 100], [80, 100, 70, 100]]

    supplier_transfer_limit = [1, 2]

    supplier_selection_contract = SupplierSelectionModel(
        price,
        demand,
        capacity=capacity,
        supplier_transfer_limit=supplier_transfer_limit,
        share=share,
    )

    supplier_selection_contract.set_volume_constraint(1, 3, 2, 70)
    supplier_selection_contract.minimise_cost()
    work_details = supplier_selection_contract.return_volume_value_details()
    assert work_details == [
        [[58, 59, 61], [20, 30, 40], [46, 44, 38], [0, 0, 10]],
        [[242, 251, 259], [0, 0, 0], [104, 101, 92], [80, 80, 70]],
    ]


def test_trust():
    price = [
        [[60, 62, 64], [605, 610, 615], [95, 96, 97], [75, 75, 75]],
        [[50, 55, 60], [615, 610, 605], [98, 97, 96], [60, 70, 80]],
    ]

    demand = [[300, 310, 320], [20, 30, 40], [150, 145, 130], [80, 80, 80]]

    capacity = [[4, 4, 4], [3, 3, 3]]

    share = [[100, 100, 30, 100], [80, 100, 70, 100]]

    supplier_transfer_limit = [1, 2]

    min_units = [
        [[100, 100, 100], [5, 5, 5], [20, 25, 30], [15, 15, 15]],
        [[100, 100, 100], [5, 5, 5], [20, 25, 30], [15, 15, 15]],
    ]

    trust = [[True, False, True, True], [True, True, True, False]]

    supplier_selection_trust = SupplierSelectionModel(
        price,
        demand,
        capacity=capacity,
        supplier_transfer_limit=supplier_transfer_limit,
        share=share,
        minimum_units=min_units,
        trust=trust,
    )
    supplier_selection_trust.minimise_cost()
    work_details = supplier_selection_trust.return_volume_value_details()
    assert work_details == [
        [[100, 100, 100], [0, 0, 0], [46, 44, 38], [80, 80, 80]],
        [[200, 210, 220], [20, 30, 40], [104, 101, 92], [0, 0, 0]],
    ]


def test_global_transfer_limit():
    (
        price,
        demand,
        capacity,
        share,
        supplier_transfer_limit,
        min_units,
        trust,
    ) = generate_supplier_selector_variables(
        n_suppliers=5, n_parts=25, n_years=10, print_data=False, seed_value=2
    )

    supplier_selection_gtl = SupplierSelectionModel(
        price,
        demand,
        capacity=capacity,
        supplier_transfer_limit=supplier_transfer_limit,
        share=share,
        global_transfer_limit=1,
        minimum_units=min_units,
        trust=trust,
    )

    supplier_selection_gtl.minimise_cost()
    work_details = supplier_selection_gtl.return_volume_value_details()
    assert work_details == [
        [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [30, 29, 260, 109, 248, 107, 0, 0, 0, 0],
            [299, 291, 276, 261, 255, 271, 269, 273, 282, 202],
            [10, 32, 26, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [21, 39, 40, 136, 139, 142, 135, 133, 134, 139],
            [109, 118, 52, 48, 51, 0, 0, 0, 0, 0],
            [203, 189, 187, 174, 174, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [21, 22, 61, 61, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [9, 31, 27, 28, 29, 31, 29, 22, 19, 18],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [25, 24, 22, 87, 87, 84, 84, 84, 87, 98],
            [21, 20, 21, 64, 22, 65, 23, 23, 22, 93],
            [176, 174, 168, 66, 155, 153, 63, 17, 17, 151],
            [27, 7, 7, 7, 63, 24, 8, 83, 89, 89],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [17, 18, 52, 17, 53, 47, 46, 15, 16, 17],
            [204, 206, 208, 200, 196, 204, 198, 208, 203, 207],
        ],
        [
            [54, 17, 142, 139, 0, 0, 0, 0, 0, 0],
            [93, 104, 14, 106, 37, 94, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [186, 0, 0, 0, 0, 0, 111, 176, 115, 115],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [44, 37, 37, 40, 46, 48, 58, 65, 67, 65],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [18, 57, 109, 101, 106, 111, 106, 104, 96, 98],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 26, 174, 170, 158, 159, 159, 167, 173, 172],
            [0, 0, 0, 0, 24, 143, 153, 160, 0, 0],
            [72, 65, 49, 16, 35, 18, 17, 17, 20, 16],
            [0, 0, 20, 61, 66, 63, 22, 21, 61, 61],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [9, 60, 52, 54, 57, 62, 56, 7, 6, 37],
            [9, 9, 25, 9, 12, 12, 34, 34, 10, 33],
            [73, 68, 62, 0, 0, 0, 0, 0, 0, 0],
            [125, 120, 129, 133, 134, 134, 141, 139, 136, 144],
            [0, 0, 0, 0, 0, 0, 0, 50, 105, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [215, 215, 218, 216, 210, 196, 193, 198, 185, 187],
            [71, 63, 73, 68, 64, 65, 60, 61, 64, 63],
            [100, 105, 99, 102, 67, 59, 59, 87, 92, 99],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
        [
            [113, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [8, 8, 20, 16, 9, 5, 4, 2, 1, 0],
            [59, 233, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [10, 10, 8, 42, 34, 27, 28, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [21, 21, 21, 22, 24, 24, 23, 22, 22, 23],
            [53, 19, 18, 17, 18, 72, 68, 67, 63, 63],
            [23, 21, 21, 19, 19, 190, 185, 180, 188, 195],
            [212, 151, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 75, 80, 83, 26, 75],
            [8, 7, 6, 23, 4, 26, 26, 26, 31, 24],
            [21, 22, 61, 20, 22, 63, 22, 21, 61, 61],
            [15, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [65, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [53, 56, 50, 56, 76, 75, 70, 68, 62, 70],
            [151, 143, 131, 135, 136, 130, 130, 129, 135, 152],
            [60, 58, 63, 22, 65, 22, 68, 66, 65, 0],
            [0, 0, 0, 101, 17, 17, 97, 104, 51, 0],
            [9, 22, 22, 21, 8, 49, 24, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [110, 98, 113, 105, 99, 100, 92, 93, 99, 96],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
        [
            [0, 0, 0, 0, 0, 0, 0, 0, 88, 93],
            [12, 13, 87, 13, 78, 12, 41, 40, 48, 71],
            [8, 47, 42, 32, 19, 11, 9, 5, 3, 1],
            [30, 29, 29, 169, 28, 167, 172, 114, 179, 178],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [10, 10, 42, 7, 17, 4, 14, 0, 0, 0],
            [7, 6, 6, 7, 8, 8, 10, 11, 11, 43],
            [106, 125, 126, 43, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [241, 237, 245, 248, 220, 24, 26, 27, 237, 168],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [30, 24, 18, 24, 21, 36, 51, 54, 53, 62],
            [9, 10, 9, 9, 10, 10, 10, 42, 37, 6],
            [17, 19, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [56, 45, 44, 42, 8, 8, 48, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [52, 55, 17, 53, 53, 47, 46, 45, 48, 52],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
        [
            [19, 149, 16, 15, 157, 153, 162, 150, 57, 60],
            [12, 13, 43, 13, 13, 12, 62, 62, 75, 47],
            [66, 23, 7, 5, 4, 3, 3, 2, 2, 2],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 90],
            [74, 53, 8, 20, 6, 14, 5, 54, 45, 40],
            [22, 19, 18, 20, 23, 23, 28, 31, 33, 0],
            [66, 21, 21, 22, 72, 74, 70, 69, 65, 67],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [24, 79, 77, 75, 70, 71, 70, 74, 77, 77],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [167, 171, 57, 58, 128, 80, 174, 171, 78, 78],
            [5, 16, 13, 16, 15, 24, 33, 36, 35, 40],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [9, 9, 8, 28, 37, 37, 12, 11, 31, 12],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
    ]
