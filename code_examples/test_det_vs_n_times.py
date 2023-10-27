#!/usr/bin/env python3
import numpy as np
import os, sys
sys.path.append(os.getcwd())
from eDPM import *
import time


def baranyi_roberts_ode(t, x, u, p, ode_args):
    x1, x2 = x
    (Temp,) = u
    (x_max, b, Temp_min) = p
    # Define the maximum growth rate
    mu_max = b**2 * (Temp - Temp_min)**2
    return [
        mu_max * (x2/(x2 + 1)) * (1 - x1/x_max) * x1,           # f1
        mu_max * x2                                             # f2
    ]

def ode_dfdp(t, x, u, p, ode_args):
    x1, x2 = x
    (Temp,) = u
    (x_max, b, Temp_min) = p
    mu_max = b**2 * (Temp - Temp_min)**2
    return [
        [
            mu_max * (x2/(x2 + 1)) * (x1/x_max)**2,             # df1/dx_max
             2 * b * (Temp - Temp_min)**2 * (x2/(x2 + 1))
                * (1 - x1/x_max)*x1,                            # df1/db
            -2 * b**2 * (Temp - Temp_min) * (x2/(x2 + 1))
                * (1 - x1/x_max)*x1                             # df1/dTemp_min
        ],
        [
            0,                                                  # df2/dx_max
            2 * b * (Temp - Temp_min)**2 * x2,                  # df2/db
            -2 * b**2 * (Temp - Temp_min) * x2                   # df2/dTemp_min
        ]
    ]

def ode_dfdx(t, x, u, p, ode_args):
    x1, x2 = x
    (Temp,) = u
    (x_max, b, Temp_min) = p
    mu_max = b**2 * (Temp - Temp_min)**2
    return [
        [
            mu_max * (x2/(x2 + 1)) * (1 - 2*x1/x_max),          # df1/dx1
            mu_max * 1/(x2 + 1)**2 * (1 - x1/x_max)*x1          # df1/dx2
        ],
        [
            0,                                                  # df2/dx1
            mu_max                                              # df2/dx2
        ]
    ]

def obs_fun(t, x, u, p, ode_args):
    x1, x2 = x
    (Temp,) = u
    (x_max, b, Temp_min) = p
    return [
        x1
    ]

def obs_dgdp(t, x, u, p, ode_args):
    x1, x2 = x
    (Temp,) = u
    (x_max, b, Temp_min) = p
    return [
        [0, 0, 0]
    ]

def obs_dgdx(t, x, u, p, ode_args):
    x1, x2 = x
    (Temp,) = u
    (x_max, b, Temp_min) = p
    return [
        [1, 0]
    ]


if __name__ == "__main__":
    start_time = time.time()

    # Parameters, ode_args and initial conditions were derived from K. Grijspeerdt1 and P. Vanrolleghem (1999) results
    # for Salmonella enteritidis growth curve in egg yolk at 30 C

    # Define parameters
    # Define parameters
    p = (2e4, 0.02, -5.5) # (x_max, b, T_min)

    # Define initial conditions
    x0 = np.array([50., 1.])

    # Define interval and number of sampling points for times
    n_times = np.linspace(1, 6, 6, dtype=int)
    # times = (0.0, 20.0, n_times)
    #times = {"lb": 0.0, "ub": 10.0, "n": n_times}

    # Define explicit temperature points
    Temp_low = 2.0
    Temp_high = 12.0
    n_Temp = [2]

    # Summarize all input definitions in list (only temperatures)
    #inputs = [[
    #    {"lb": Temp_low, "ub": Temp_high, "n": nT},
    #] for nT in n_Temp]

    det = []
    for nT in n_Temp:
        inputs = [
        {"lb": Temp_low, "ub": Temp_high, "n": nT},
        ]

        det_nT = []
        for nt in n_times:
            print(nt)
            times = {"lb": 0.0, "ub": 10.0, "n": nt}

            fsm = FisherModel(
                ode_x0=x0,
                ode_t0=0.0,
                ode_fun=baranyi_roberts_ode,
                ode_dfdx=ode_dfdx,
                ode_dfdp=ode_dfdp,
                ode_initial=x0,
                times=times,
                inputs=inputs,
                parameters=p,
                obs_fun=obs_fun,
                obs_dgdx=obs_dgdx,
                obs_dgdp=obs_dgdp,
                covariance={"abs": 0.3, "rel": 0.1}
            )

            fsr = find_optimal(
                fsm,
                relative_sensitivities=True,
                recombination=0.7,
                mutation=(0.1, 0.8),
                workers=18,
                popsize=10,
                polish=False,
                maxiter=50
            )

            det_nT.append(fsr.criterion)
            print(f"nT = {nT}, nt = {nt} rank S = {np.linalg.matrix_rank(fsr.S)}\n\n")
        det.append(det_nT)

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(n_times, det_nT, alpha=1, color="#0099e5", marker='o', markersize=15, label="det (F)")
        ax.set_yscale('log')
        ax.set_ylabel("Determinant", fontsize=16)
        ax.set_xlabel("Number of measured times", fontsize=16)
        ax.tick_params(axis="y", labelsize=14)
        ax.tick_params(axis="x", labelsize=14)
        ax.legend(fontsize=16, framealpha=0.0)
        fig.savefig(f"out/baranyi_model/det_vs_ntimes.pdf", bbox_inches='tight')
        # Remove figure to free space
        plt.close(fig)


    # Plot all ODE results with chosen time points
    # for different data points
    conditions = f"rel_sensit_cont_{n_times}times_{n_Temp}temps"
    #plot_all_solutions(fsr, outdir="out/baranyi_model", additional_name=conditions)
    #json_dump(fsr, f"out/baranyi_model/baranyi_roberts_ode_fisher_determinant_{conditions}.json")

    
