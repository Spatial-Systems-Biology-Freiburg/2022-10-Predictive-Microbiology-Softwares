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
    p = (2e4, 0.02, -5.5) # (x_max, b, T_min)

    # Define initial conditions
    x0 = np.array([50., 1.])

    # Define interval and number of sampling points for times
    n_times = 2
    # times = (0.0, 20.0, n_times)
    times = {"lb": 0., "ub": 100., "n": n_times}

    # Define explicit temperature points
    Temp_low = 2.0
    Temp_high = 12.0
    n_Temp = 2

    # Summarize all input definitions in list (only temperatures)
    inputs = [
        {"lb": Temp_low, "ub": Temp_high, "n": n_Temp},
    ]

    # Create the FisherModel which serves as the entry point
    #  for the solving and optimization algorithms
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
        obs_fun=[0],
        #obs_dgdx=obs_dgdx,
        #obs_dgdp=obs_dgdp,
        covariance={"abs": 1.3, "rel": 1.1}
    )

    fsr = find_optimal(
        fsm,
        relative_sensitivities=True,
        recombination=0.7,
        mutation=(0.1, 0.8),
        workers=-1,
        popsize=12,
        polish=False,
        disp=True
    )

    end_time = time.time()
    diff = (end_time-start_time)
    #print(f"\n Optimization time: {diff:.2f} s")

    #print("rank S = ", np.linalg.matrix_rank(fsr.S))

    # Plot all ODE results with chosen time points
    # for different data points
    conditions = f"rel_sensit_cont_{n_times}times_{n_Temp}temps"
    plot_all_solutions(fsr, outdir="out/extra", additional_name=conditions, file_format="pdf")
    json_dump(fsr, f"out/extra/baranyi_roberts_ode_fisher_determinant_{conditions}.json")

    check = check_if_identifiable(fsr)
