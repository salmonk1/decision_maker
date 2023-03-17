import numpy as np
from ortools.sat.python import cp_model

from decision_engine_optimiser.utils import timeit


class MinimalSupplierSelectionModel:
    def __init__(self, price, demand, capacity=None, share=None):
        self.status = None
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

        self.price = price
        self.demand = demand
        self.capacity = capacity
        self.share = share
        self.n_parts = len(self.demand)
        self.n_suppliers = len(self.price)

        self.volume = self._create_volume_matrix()
        self.assigned = self._create_assigned_matrix()

        self._link_volume_to_assigned()
        self._add_constraint_volume()
        if self.capacity != None:
            self._add_constraint_manufacturing_capacity()
        if self.share != None:
            self._add_constraint_part_share()

        self.model.Minimize(self._compute_cost())

    def _create_volume_matrix(self):
        """
        Volume S{supplier}P{part}
        """
        s = []
        for supplier in range(self.n_suppliers):
            p = []
            for part in range(self.n_parts):
                p.append(
                    self.model.NewIntVar(0, 500, "Volume S{}P{}".format(supplier, part))
                )
            s.append(p)
        return s

    def _create_assigned_matrix(self):
        """
        True if a part has been assigned to a supplier, else false
        """
        s = []
        for supplier in range(self.n_suppliers):
            p = []
            for part in range(self.n_parts):
                p.append(
                    self.model.NewBoolVar("Assigned S{}P{}".format(supplier, part))
                )
            s.append(p)
        return s

    def _link_volume_to_assigned(self):
        """
        Link the volume and assigned matrix

        A channelling constraint links variables inside a model.
        They're used when you want to express a complicated relationship
        between variables, such as "if this variable satisfies a condition,
        force another variable to a particular value".

        if volume[supplier][part] > 0:
            assigned[supplier][part] = True
        """
        for supplier in range(self.n_suppliers):
            for part in range(self.n_parts):
                self.model.Add(self.volume[supplier][part] > 0).OnlyEnforceIf(
                    self.assigned[supplier][part]
                )
                self.model.Add(self.volume[supplier][part] == 0).OnlyEnforceIf(
                    self.assigned[supplier][part].Not()
                )

    def _add_constraint_volume(self):
        """
        Add a constraint to ensure that the manufactured volume of a part
        is equal to the demand
        """
        for supplier in range(self.n_suppliers):
            for part in range(self.n_parts):
                self.model.Add(
                    sum(
                        self.volume[supplier][part]
                        for supplier in range(self.n_suppliers)
                    )
                    == self.demand[part]
                )

    def _add_constraint_manufacturing_capacity(self):
        """
        Add a constraint to ensure that a manufacturer is not assigned more parts
        than that defined by their manufacturing capacity
        """
        for supplier in range(self.n_suppliers):
            self.model.Add(
                sum(self.assigned[supplier][part] for part in range(self.n_parts))
                <= self.capacity[supplier]
            )

    def _add_constraint_part_share(self):
        """
        Add a constraint to ensure that the share of a part
        assigned to a supplier is less than the limit
        """
        for supplier in range(self.n_suppliers):
            for part in range(self.n_parts):
                target = self.model.NewIntVar(0, 100, "volume/demand * 100")
                numerator = self.volume[supplier][part] * 100
                denominator = self.demand[part]
                self.model.AddDivisionEquality(target, numerator, denominator)
                self.model.Add(target <= self.share[supplier][part])

    def _compute_cost(self):
        cost = 0
        for supplier in range(self.n_suppliers):
            for part in range(self.n_parts):
                cost += self.price[supplier][part] * self.volume[supplier][part]
        return cost

    def _print_solution(self):
        for supplier in range(self.n_suppliers):
            print("\nSupplier {}\n----------".format(supplier + 1))
            for part in range(self.n_parts):
                print(
                    "Part {} units: {}".format(
                        part + 1, self.solver.Value(self.volume[supplier][part])
                    )
                )

    def minimise_cost(self, print=False):
        """
        Solve the optimisation problem: minimise
        the cost
        """
        self.status = self.solver.Solve(self.model)
        if print:
            self.print_status()
        return self.status

    def print_status(self):
        if self.status is None:
            raise ValueError("optimiser has not run")
        if self.status == cp_model.OPTIMAL:
            print(
                "\nOptimal solution found: cost - £{:,.2f}".format(
                    self.solver.ObjectiveValue()
                )
            )
            self._print_solution()
        elif self.status == cp_model.FEASIBLE:
            print("Feasible solution found")
        else:
            print("No solution found")

    def return_volume(self, supplier, part):
        """
        returns the volume matrix
        """
        return self.solver.Value(self.volume[supplier][part])

    def return_total_cost(self):
        """
        returns total cost
        """
        return self.solver.ObjectiveValue()

    def return_supplier_cost(self):
        """
        returns total cost per supplier
        """
        cost = []
        for supplier in range(self.n_suppliers):
            cost_per_part = 0
            for part in range(self.n_parts):
                cost_per_part += self.price[supplier][part] * self.solver.Value(
                    self.volume[supplier][part]
                )
            cost.append(cost_per_part)
        return cost

    def return_work_value_details(self):
        """
        Returns detailed work value per supplier
        """
        if self.status is None:
            raise ValueError("optimiser has not run")
        elif not (self.status == cp_model.OPTIMAL or self.status == cp_model.FEASIBLE):
            raise ValueError("optimiser has not found a solution")
        all_details = []
        for supplier in range(self.n_suppliers):
            # print("\nSupplier {:>2}: \n------------\n".format(supplier))
            details = []
            for part in range(self.n_parts):
                value = self.price[supplier][part] * self.solver.Value(
                    self.volume[supplier][part]
                )
                # print("Part {:>2}: £{:>12,.2f}".format(part, value))
                details.append(value)
            all_details.append(details)
        return all_details

    def return_volume_value_details(self):
        """
        Returns detailed work value per supplier
        """
        if self.status is None:
            raise ValueError("optimiser has not run")
        elif not (self.status == cp_model.OPTIMAL or self.status == cp_model.FEASIBLE):
            raise ValueError("optimiser has not found a solution")
        all_details = []
        for supplier in range(self.n_suppliers):
            # print("\nSupplier {:>2}: \n------------\n".format(supplier))
            details = []
            for part in range(self.n_parts):
                value = self.return_volume(supplier=supplier, part=part)
                # print("Part {:>2}: £{:>12,.2f}".format(part, value))
                details.append(value)
            all_details.append(details)
        return all_details


class SupplierSelectionModel:
    """
    Supplier selection model class

    Attributes
    ----------
    price : list
        List of prices for every supplier, part and year

    demand : list
        The demand (number of units needed) for every part in every year

    capacity : list

    supplier_transfer_limit : list

    global_transfer_limit : int

    share : list

    minimum_units : list

    trust : list

    n_threads : int

    Methods
    -------

    Notes
    -----
    - TODO: look at using product() from itertools to avoid nested for loops
    """

    def __init__(
        self,
        price,
        demand,
        capacity=None,
        supplier_transfer_limit=None,
        global_transfer_limit=None,
        share=None,
        minimum_units=None,
        trust=None,
        n_threads=8,
    ):
        self.status = None
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.solver.parameters.num_search_workers = n_threads

        self.price = price
        self.demand = demand
        self.capacity = capacity
        self.supplier_transfer_limit = supplier_transfer_limit
        self.global_transfer_limit = global_transfer_limit
        self.share = share
        self.minimum_units = minimum_units
        self.trust = trust
        self.n_suppliers = len(self.price)
        self.n_parts = len(self.price[0])
        self.n_years = len(self.price[0][0])

        self.volume = self._create_volume_matrix()
        self.assigned = self._create_assigned_matrix()

        self._link_volume_to_assigned()
        self._add_constraint_volume()
        if self.capacity != None:
            self._add_constraint_manufacturing_capacity()
        if self.supplier_transfer_limit != None:
            self.transferred = self._create_transferred_matrix()
            self._link_assigned_to_transferred()
            self._add_constraint_supplier_transfer_limit()
        if self.global_transfer_limit != None:
            self._add_constraint_global_transfer_limit()
        if self.share != None:
            self._add_constraint_part_share()
        if self.minimum_units != None:
            self._add_constraint_minimum_units()
        if self.trust != None:
            self.t = self._create_intermediate_trust_matrix()
            self._add_constraint_trust()

    def __sub__(self, other):
        """
        Difference of two objects (Scenario A and Scenario B)
        """
        for supplier in range(self.n_suppliers):
            print("\nSupplier {:>2}: \n------------\n".format(supplier + 1))
            for part in range(self.n_parts):
                value = 0
                for year in range(self.n_years):
                    value += (
                        self.price[supplier][part][year]
                        * self.solver.Value(self.volume[supplier][part][year])
                    ) - (
                        other.price[supplier][part][year]
                        * other.solver.Value(other.volume[supplier][part][year])
                    )
                print("Part {:>2}: £{:>12,.2f}".format(part + 1, value))

    def _create_volume_matrix(self):
        """
        Volume S{supplier}P{part}Y{year}
        """
        s = []
        for supplier in range(self.n_suppliers):
            p = []
            for part in range(self.n_parts):
                y = []
                for year in range(self.n_years):
                    y.append(
                        self.model.NewIntVar(
                            0, 500, "Volume S{}P{}Y{}".format(supplier, part, year)
                        )
                    )
                p.append(y)
            s.append(p)
        return s

    def _create_assigned_matrix(self):
        """
        True if a part has been assigned to a supplier, else false
        """
        s = []
        for supplier in range(self.n_suppliers):
            p = []
            for part in range(self.n_parts):
                y = []
                for year in range(self.n_years):
                    y.append(
                        self.model.NewBoolVar(
                            "Assigned S{}P{}Y{}".format(supplier, part, year)
                        )
                    )
                p.append(y)
            s.append(p)
        return s

    def _create_transferred_matrix(self):
        """
        True if a part has been transferred to a different supplier, else false
        """
        s = []
        for supplier in range(self.n_suppliers):
            p = []
            for part in range(self.n_parts):
                y = []
                for year in range(self.n_years):
                    y.append(
                        self.model.NewBoolVar(
                            "Transferred S{}P{}Y{}".format(supplier, part, year)
                        )
                    )
                p.append(y)
            s.append(p)
        return s

    def _create_intermediate_trust_matrix(self):
        """
        Create an intermediate boolean variable to represent supplier trust

        True - supplier x is trusted to manufacture part y
        False - supplier x is not trusted to manufacture part y
        """
        s = []
        for supplier in range(self.n_suppliers):
            p = []
            for part in range(self.n_parts):
                p.append(self.model.NewBoolVar("Trust S{}P{}".format(supplier, part)))
            s.append(p)
        return s

    def _link_volume_to_assigned(self):
        """
        Link the volume and assigned matrix

        if volume[supplier][part][year] > 0:
            assigned[supplier][part][year] = True
        """
        for supplier in range(self.n_suppliers):
            for part in range(self.n_parts):
                for year in range(self.n_years):
                    self.model.Add(self.volume[supplier][part][year] > 0).OnlyEnforceIf(
                        self.assigned[supplier][part][year]
                    )
                    self.model.Add(
                        self.volume[supplier][part][year] == 0
                    ).OnlyEnforceIf(self.assigned[supplier][part][year].Not())

    def _link_assigned_to_transferred(self):
        """
        Constraint 1 : supplier remains the same or the supplier is exited
        Constraint 2 : supplier is entered

        if assigned[supplier][part][year-1] >= assigned[supplier][part][year]:
            transferred[supplier][part][year] = False

        if assigned[supplier][part][year-1] != assigned[supplier][part][year]:
            transferred[supplier][part][year] = True

        Supplier exited or entered
        """
        for supplier in range(self.n_suppliers):
            for part in range(self.n_parts):
                for year in range(1, self.n_years):
                    self.model.Add(
                        self.assigned[supplier][part][year - 1]
                        >= self.assigned[supplier][part][year]
                    ).OnlyEnforceIf(self.transferred[supplier][part][year].Not())

                    self.model.Add(
                        self.assigned[supplier][part][year - 1]
                        != self.assigned[supplier][part][year]
                    ).OnlyEnforceIf(self.transferred[supplier][part][year])

    def _add_constraint_volume(self):
        """
        Add a constraint to ensure that the manufactured volume of a part
        is equal to the demand
        """
        for supplier in range(self.n_suppliers):
            for part in range(self.n_parts):
                for year in range(self.n_years):
                    self.model.Add(
                        sum(
                            self.volume[supplier][part][year]
                            for supplier in range(self.n_suppliers)
                        )
                        == self.demand[part][year]
                    )

    def _add_constraint_manufacturing_capacity(self):
        """
        Add a constraint to ensure that a manufacturer is not assigned more
        parts than that defined by their manufacturing capacity
        """
        for supplier in range(self.n_suppliers):
            for year in range(self.n_years):
                self.model.Add(
                    sum(
                        self.assigned[supplier][part][year]
                        for part in range(self.n_parts)
                    )
                    <= self.capacity[supplier][year]
                )

    def _add_constraint_part_share(self):
        """
        Add a constraint to ensure that the share of a part
        assigned to a supplier is less than the limit
        """
        for supplier in range(self.n_suppliers):
            for part in range(self.n_parts):
                for year in range(self.n_years):
                    target = self.model.NewIntVar(0, 100, "volume/demand * 100")
                    numerator = self.volume[supplier][part][year] * 100
                    denominator = self.demand[part][year]
                    self.model.AddDivisionEquality(target, numerator, denominator)
                    self.model.Add(target <= self.share[supplier][part])

    def _add_constraint_supplier_transfer_limit(self):
        """
        Add a constraint to ensure that the number of parts transferred to a
        supplier per year is less than the specified limit
        """
        for supplier in range(self.n_suppliers):
            for year in range(self.n_years):
                self.model.Add(
                    sum(
                        self.transferred[supplier][part][year]
                        for part in range(self.n_parts)
                    )
                    <= self.supplier_transfer_limit[supplier]
                )

    def _add_constraint_global_transfer_limit(self):
        """
        Add a constraint to ensure that the number of parts transferred
        globally is less than the specified limit
        """
        for year in range(self.n_years):
            self.model.Add(
                sum(
                    sum(
                        self.transferred[supplier][part][year]
                        for supplier in range(self.n_suppliers)
                    )
                    for part in range(self.n_parts)
                )
                <= self.global_transfer_limit
            )

    def _add_constraint_minimum_units(self):
        """
        Add a constraint to enforce a minimum number of units - a supplier
        will only accept a contract to manufacture a part if the
        number of units awarded exceeds a minimum threshold

        if assigned[supplier][part][year] == True:
            self.volume[supplier][part][year]
                        > self.minimum_units[supplier][part][year]
        """
        for supplier in range(self.n_suppliers):
            for part in range(self.n_parts):
                for year in range(self.n_years):
                    self.model.Add(
                        self.volume[supplier][part][year]
                        >= self.minimum_units[supplier][part][year]
                    ).OnlyEnforceIf(self.assigned[supplier][part][year])

    def _add_constraint_trust(self):
        """
        Add a constraint that a supplier can only be assigned to manufacture
        a part if they are trusted - supplier x cannot be assigned part y if
        trust is False

        if trust is False:
            supplier x cannot be assigned part y

        Notes
        -----
        t = (self.trust[supplier][part] == 0)
        self.model.Add(self.volume[supplier][part][year] == 0).OnlyEnforceIf(t)
        """
        for supplier in range(self.n_suppliers):
            for part in range(self.n_parts):
                self.model.Add(self.trust[supplier][part] == 0).OnlyEnforceIf(
                    self.t[supplier][part]
                )  # if trust is False
                self.model.Add(self.trust[supplier][part] == 1).OnlyEnforceIf(
                    self.t[supplier][part].Not()
                )  # if trust is True
                for year in range(self.n_years):
                    self.model.Add(
                        self.volume[supplier][part][year] == 0
                    ).OnlyEnforceIf(self.t[supplier][part])
                    self.model.Add(
                        self.volume[supplier][part][year] >= 0
                    ).OnlyEnforceIf(self.t[supplier][part].Not())

    def _compute_cost(self):
        cost = 0
        for supplier in range(self.n_suppliers):
            for part in range(self.n_parts):
                for year in range(self.n_years):
                    cost += (
                        self.price[supplier][part][year]
                        * self.volume[supplier][part][year]
                    )
        return cost

    def print_solution(
        self, volume=False, price=False, assigned=False, transferred=False
    ):
        for part in range(self.n_parts):
            self._print_header(part)
            for supplier in range(self.n_suppliers):
                v = []
                p = []
                a = []
                t = []
                for year in range(self.n_years):
                    if volume:
                        v.append(self.solver.Value(self.volume[supplier][part][year]))
                    if price:
                        p.append(self.solver.Value(self.price[supplier][part][year]))
                    if assigned:
                        a.append(self.solver.Value(self.assigned[supplier][part][year]))
                    if transferred:
                        t.append(
                            self.solver.Value(self.transferred[supplier][part][year])
                        )
                self._print_line(supplier, p, v, a, t)

    def _print_header(self, part):
        print("\n\nPart {:>2}     ".format(part + 1), end="")
        for year in range(self.n_years):
            if year < self.n_years - 1:
                print("{:>10}".format(year + 1), end="")
            if year == self.n_years - 1:
                print("{:>10}".format(year + 1))
        print("-------")

    def _print_line(self, supplier, *args):
        print("\nSupplier {:>2}:".format(supplier + 1), end="")
        count = 0
        for arg in args:
            if arg:
                count += 1
                if count == 1:
                    for year in range(self.n_years):
                        if year < self.n_years - 1:
                            print("{:>10}".format(arg[year]), end="")
                        if year == self.n_years - 1:
                            print("{:>10}".format(arg[year]))
                elif count > 1:
                    print("            ", end="")
                    for year in range(self.n_years):
                        if year < self.n_years - 1:
                            print("{:>10}".format(arg[year]), end="")
                        if year == self.n_years - 1:
                            print("{:>10}".format(arg[year]))

    def print_work_value(self):
        for supplier in range(self.n_suppliers):
            value = 0
            print("\nSupplier {:>2}: ".format(supplier + 1), end="")
            for part in range(self.n_parts):
                for year in range(self.n_years):
                    value += self.price[supplier][part][year] * self.solver.Value(
                        self.volume[supplier][part][year]
                    )
            print("£{:>12,.2f}".format(value))

    def print_work_value_detailed(self):
        for supplier in range(self.n_suppliers):
            print("\nSupplier {:>2}: \n------------\n".format(supplier + 1))
            for part in range(self.n_parts):
                value = 0
                for year in range(self.n_years):
                    value += self.price[supplier][part][year] * self.solver.Value(
                        self.volume[supplier][part][year]
                    )
                print("Part {:>2}: £{:>12,.2f}".format(part + 1, value))

    def _save_solution_to_pandas_df(self):
        pass

    @timeit
    def minimise_cost(self, print=False):
        """
        Solve the optimisation problem: minimise
        the cost
        """
        self.model.Minimize(self._compute_cost())
        self.status = self.solver.Solve(self.model)
        if print:
            self.print_status()
        return self.status

    def print_status(self):
        if self.status is None:
            raise ValueError("optimiser has not run")
        if self.status == cp_model.OPTIMAL:
            print(
                "\nOptimal solution found: cost - £{:,.2f}".format(
                    self.solver.ObjectiveValue()
                )
            )
        elif self.status == cp_model.FEASIBLE:
            print("Feasible solution found")
        else:
            print("No solution found")

    def set_volume_constraint(self, supplier, part, year, vol):
        """
        Setter function - set a constraint on the volume for a
        given supplier, part and year
        """
        self.model.Add(self.volume[supplier][part][year] == vol)

    def return_volume(self, supplier, part):
        if supplier >= len(self.volume):
            raise ValueError("Out of range")
        if part >= len(self.volume[supplier]):
            raise ValueError("Out of range")
        return self.solver.Value(self.volume[supplier][part])

    def _value_to_ndarray(self):
        """
        Convert a list of values to a numpy array
        """
        value = np.zeros([self.n_suppliers, self.n_parts])
        for supplier in range(self.n_suppliers):
            for part in range(self.n_parts):
                for year in range(self.n_years):
                    value[supplier][part] += self.price[supplier][part][
                        year
                    ] * self.solver.Value(self.volume[supplier][part][year])
        return value

    def _heatmap(
        self,
        data,
        row_labels,
        col_labels,
        vmin=0,
        vmax=0,
        ax=None,
        cbar_kw=None,
        cbarlabel="",
        **kwargs
    ):
        """
        Create a heatmap from a numpy array and two lists of labels.

        Parameters
        ----------
        data : ndarray
            A 2D numpy array of shape (M, N)

        row_labels : list
            A list or array of length M with the labels for the rows.

        col_labels : list
            A list or array of length N with the labels for the columns.

        ax : matplotlib.axes.Axes
            A `matplotlib.axes.Axes` instance to which the heatmap is plotted.
            If not provided, use current axes or create a new one. Optional.

        cbar_kw : dict
            A dictionary with arguments to `matplotlib.Figure.colorbar`.
            Optional.

        cbarlabel : str
            The label for the colorbar. Optional.

        **kwargs
            All other arguments are forwarded to `imshow`.

        """

        import matplotlib.pyplot as plt

        plt.rcParams.update(
            {
                "text.usetex": True,
                "font.family": "sans-serif",
                "font.sans-serif": ["Times New Roman"],
            }
        )
        plt.rcParams["font.family"] = "Times New Roman"

        if ax is None:
            ax = plt.gca()

        if cbar_kw is None:
            cbar_kw = {}

        # Plot the heatmap
        im = ax.imshow(data, vmin=vmin, vmax=vmax, **kwargs)

        # Create colorbar
        cbar = ax.figure.colorbar(
            im,
            ax=ax,
            location="bottom",
            orientation="horizontal",
            format="£{x:,.0f}",
            **cbar_kw
        )

        # Show all ticks and label them with the respective list entries.
        ax.set_xticks(np.arange(data.shape[1]), labels=col_labels)
        ax.set_yticks(np.arange(data.shape[0]), labels=row_labels)

        # Let the horizontal axes labeling appear on top.
        ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)

        # Rotate the tick labels and set their alignment.
        plt.setp(ax.get_xticklabels(), rotation=-30, ha="right", rotation_mode="anchor")

        # Turn spines off and create white grid.
        ax.spines[:].set_visible(False)

        ax.set_xticks(np.arange(data.shape[1] + 1) - 0.5, minor=True)
        ax.set_yticks(np.arange(data.shape[0] + 1) - 0.5, minor=True)
        ax.grid(which="minor", color="w", linestyle="-", linewidth=3)
        ax.tick_params(which="minor", bottom=False, left=False)

    def plot_heatmap(self, name=None, save=False):
        """
        Plot a heatmap of suppliers, parts and the value of work won (£)
        """
        value_array = self._value_to_ndarray()
        fig, ax = plt.subplots()
        if name != None:
            ax.set_title(name, pad=35)
        self._heatmap(
            value_array,
            [s + 1 for s in range(self.n_suppliers)],  # suppliers
            [p + 1 for p in range(self.n_parts)],  # parts
            vmax=np.max(value_array),
            ax=ax,
            cmap="Greys",
            cbarlabel="value (£)",
        )
        if save:
            plt.savefig("heatmap.png", dpi=300, bbox_inches="tight")

    def heatmap_difference(self, scenario, name=None, save=False):
        """
        Plot a heatmap of suppliers, parts and the value of work won (£)
        """
        import matplotlib.pyplot as plt

        plt.rcParams.update(
            {
                "text.usetex": True,
                "font.family": "sans-serif",
                "font.sans-serif": ["Times New Roman"],
            }
        )
        plt.rcParams["font.family"] = "Times New Roman"

        a = self._value_to_ndarray()
        b = scenario._value_to_ndarray()
        c = a - b
        limit = np.max(np.abs([np.max(c), np.min(c)]))

        fig, ax = plt.subplots()
        if name != None:
            ax.set_title(name, pad=35)
        self._heatmap(
            c,
            [s + 1 for s in range(self.n_suppliers)],  # suppliers
            [p + 1 for p in range(self.n_parts)],  # parts
            vmin=-limit,
            vmax=limit,
            ax=ax,
            cmap="PiYG",
            cbarlabel="value (£)",
        )
        if save:
            plt.savefig("heatmap_diff.png", dpi=300, bbox_inches="tight")

    def return_volume(self, supplier, part, year):
        """
        returns the volume matrix
        """
        if supplier >= len(self.volume):
            raise ValueError("Out of range")
        if part >= len(self.volume[supplier]):
            raise ValueError("Out of range")
        if year >= len(self.volume[supplier][part]):
            raise ValueError("Out of range")
        return self.solver.Value(self.volume[supplier][part][year])

    def return_total_cost(self):
        """
        returns total cost
        """
        return self.solver.ObjectiveValue()

    def return_supplier_cost(self):
        """
        returns total cost per supplier
        """
        cost = []
        for supplier in range(self.n_suppliers):
            cost_per_part = 0
            for part in range(self.n_parts):
                for year in range(self.n_years):
                    cost_per_part += self.price[supplier][part][
                        year
                    ] * self.solver.Value(self.volume[supplier][part][year])
            cost.append(cost_per_part)
        return cost

    def return_work_value_details(self):
        """
        Returns detailed work value per supplier
        """
        if self.status is None:
            raise ValueError("optimiser has not run")
        elif not (self.status == cp_model.OPTIMAL or self.status == cp_model.FEASIBLE):
            raise ValueError("optimiser has not found a solution")
        all_details = []
        for supplier in range(self.n_suppliers):
            # print("\nSupplier {:>2}: \n------------\n".format(supplier))
            details = []
            for part in range(self.n_parts):
                value = 0
                for year in range(self.n_years):
                    value += self.price[supplier][part][year] * self.solver.Value(
                        self.volume[supplier][part][year]
                    )
                # print("Part {:>2}: £{:>12,.2f}".format(part, value))
                details.append(value)
            all_details.append(details)
        return all_details

    def return_volume_value_details(self):
        """
        Returns detailed work value per supplier
        """
        if self.status is None:
            raise ValueError("optimiser has not run")
        elif not (self.status == cp_model.OPTIMAL or self.status == cp_model.FEASIBLE):
            raise ValueError("optimiser has not found a solution")

        all_details = []
        for supplier in range(self.n_suppliers):
            # print("\nSupplier {:>2}: \n------------\n".format(supplier))
            details = []
            for part in range(self.n_parts):
                value = []
                for year in range(self.n_years):
                    value.append(
                        self.return_volume(supplier=supplier, part=part, year=year)
                    )
                # print("Part {:>2}: £{:>12,.2f}".format(part, value))
                details.append(value)
            all_details.append(details)
        return all_details