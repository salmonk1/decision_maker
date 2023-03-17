import random
import copy
from functools import wraps
import time

import numpy as np


def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        func(*args, **kwargs)
        end = time.perf_counter()
        total = end - start
        print("Execution time: {:.5f} seconds".format(total))

    return wrapper


def random_walk(mean, std_dev):
    return np.rint(np.random.normal(mean, std_dev))


def brownian_motion(n_time_steps, start, mean=0, std_dev=10):
    """
    1D simulation of Brownian motion

    Parameters
    ----------
    u : int
        Displacement
    """
    u = start
    u_hist = []
    for i in range(n_time_steps):
        u += random_walk(mean, std_dev)
        u_hist.append(np.abs(u.astype(int)))
    return u_hist


def generate_supplier_selector_variables(
    min_price=1e3,
    max_price=100e3,
    min_demand=50,
    max_demand=300,
    n_suppliers=15,
    n_parts=50,
    n_years=4,
    print_data=True,
    seed_value=None,
):
    np.random.seed(seed_value)
    random.seed(seed_value)

    price = []
    start = np.random.randint(min_price, max_price, n_parts)
    for _ in range(n_suppliers):
        s = []
        for part in range(n_parts):
            y = brownian_motion(n_years, start[part], std_dev=.2e3)
            s.append(y)
        price.append(s)

    demand = []
    for _ in range(n_parts):
        y = []
        start = np.random.randint(min_demand, max_demand)
        for _ in range(n_years):
            y = brownian_motion(n_years, start)
        demand.append(y)

    minimum_units = []
    for supplier in range(n_suppliers):
        s = []
        for part in range(n_parts):
            y = []
            for year in range(n_years):
                y.append(round(demand[part][year] * 0.1))
            s.append(y)
        minimum_units.append(s)

    capacity = []
    for _ in range(n_suppliers):
        y = []
        for _ in range(n_years):
            y.append(np.random.randint(n_parts * 0.5, n_parts))
        capacity.append(y)

    share = []
    for _ in range(n_suppliers):
        s = []
        for _ in range(n_parts):
            sample = np.random.rand()
            if sample < 0.2:
                s.append(30)
            elif 0.2 <= sample < 0.7:
                s.append(60)
            else:
                s.append(100)
        share.append(s)

    trust = []
    for _ in range(n_suppliers):
        s = []
        for _ in range(n_parts):
            s.append(random.choice([0, 1, 1, 1, 1]))
        trust.append(s)

    supplier_transfer_limit = []
    for _ in range(n_suppliers):
        supplier_transfer_limit.append(np.random.randint(n_parts * 0.5, n_parts))

    if print_data:
        print(f"number of suppliers: {n_suppliers}")
        print(f"number of parts: {n_parts}")
        print(f"price: {price}")
        print(f"demand: {demand}")
        print(f"minimum units: {minimum_units}")
        print(f"capacity: {capacity}")
        print(f"share: {share}")
        print(f"supplier transfer limit: {supplier_transfer_limit}")
        print(f"Trust: {trust}")

    return price, demand, capacity, share, supplier_transfer_limit, minimum_units, trust


def compute_reduced_price(price, supplier, reduction):
    new_price = copy.deepcopy(price)
    for part in range(len(price[0])):
        for year in range(len(price[0][0])):
            new_price[supplier][part][year] = np.rint(
                price[supplier][part][year] * (1 - reduction)
            ).astype(int)
    return new_price
