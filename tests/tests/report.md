# Diff Coverage
## Diff: origin/main...HEAD, staged and unstaged changes

- optimiser/decision_engine_optimiser/__init__&#46;py (100%)
- optimiser/decision_engine_optimiser/decision_engine&#46;py (61.7%): Missing lines 162,170-171,173,185,191-195,198-199,205-210,212-214,218-220,227,229,330-335,342,598-613,616,619-625,628-645,648-653,656,659-664,667,670,681,685-688,693-694,696,706-710,716-720,723,767,769,776,778-779,781-782,785,788,798-799,802,805,808,810-813,819-823,832-833,839,841,848,850-853,855-858,868-869,876,878,880,887,893-898,901-902,908-913,915-919,923-925,932,934
- optimiser/decision_engine_optimiser/tests/test_simple_cases&#46;py (100%)
- optimiser/decision_engine_optimiser/utils&#46;py (87.8%): Missing lines 99-107

## Summary

- **Total**: 611 lines
- **Missing**: 184 lines
- **Coverage**: 69%



## optimiser/decision_engine_optimiser/decision_engine&#46;py

Lines 158-166

```python
        return self.status

    def print_status(self):
        if self.status is None:
            raise ValueError("optimiser has not run")
        if self.status == cp_model.OPTIMAL:
            print(
                "\nOptimal solution found: cost - £{:,.2f}".format(
                    self.solver.ObjectiveValue()
```


---


Lines 166-177

```python
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
```


---


Lines 181-189

```python
    def return_total_cost(self):
        """
        returns total cost
        """
        return self.solver.ObjectiveValue()

    def return_supplier_cost(self):
        """
        returns total cost per supplier
```


---


Lines 187-203

```python
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
```


---


Lines 201-224

```python
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
```


---


Lines 223-233

```python
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
```


---


Lines 326-339

```python
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
```


---


Lines 338-346

```python
                    ) - (
                        other.price[supplier][part][year]
                        * other.solver.Value(other.volume[supplier][part][year])
                    )
                print("Part {:>2}: £{:>12,.2f}".format(part + 1, value))

    def _create_volume_matrix(self):
        """
        Volume S{supplier}P{part}Y{year}
```


---


Lines 594-674

```python

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
```


---


Lines 677-700

```python
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
```


---


Lines 702-714

```python
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
```


---


Lines 712-727

```python
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
```


---


Lines 763-773

```python
            All other arguments are forwarded to `imshow`.

        """

        import matplotlib.pyplot as plt

        plt.rcParams.update(
            {
                "text.usetex": True,
                "font.family": "sans-serif",
                "font.sans-serif": ["Times New Roman"],
```


---


Lines 772-792

```python
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
```


---


Lines 794-817

```python
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
```


---


Lines 815-827

```python
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
```


---


Lines 828-837

```python
            ax=ax,
            cmap="Greys",
            cbarlabel="value (£)",
        )
        if save:
            plt.savefig("heatmap.png", dpi=300, bbox_inches="tight")

    def heatmap_difference(self, scenario, name=None, save=False):
        """
        Plot a heatmap of suppliers, parts and the value of work won (£)
```


---


Lines 835-845

```python
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
```


---


Lines 844-862

```python
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
```


---


Lines 864-873

```python
            ax=ax,
            cmap="PiYG",
            cbarlabel="value (£)",
        )
        if save:
            plt.savefig("heatmap_diff.png", dpi=300, bbox_inches="tight")

    def return_volume(self, supplier, part, year):
        """
        returns the volume matrix
```


---


Lines 872-884

```python
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
```


---


Lines 883-891

```python
    def return_total_cost(self):
        """
        returns total cost
        """
        return self.solver.ObjectiveValue()

    def return_supplier_cost(self):
        """
        returns total cost per supplier
```


---


Lines 889-906

```python
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
```


---


Lines 904-929

```python
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
```


---


Lines 928-938

```python
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
```


---



## optimiser/decision_engine_optimiser/utils&#46;py

Lines 95-110

```python
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

```


---


