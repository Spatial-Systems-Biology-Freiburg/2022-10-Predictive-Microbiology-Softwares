#!/usr/bin/env python3
import numpy as np
import os, sys
sys.path.append(os.getcwd())
from eDPM import *


def baranyi_roberts_ode(t, x, u, p, ode_args):
    x1, x2, y1, y2 = x
    (Temp, ) = u
    (xy_max, b_x, Temp_min_x, b_y, Temp_min_y, ) = p
    # Define the maximum growth rate
    mu_max_x = b_x**2 * (Temp - Temp_min_x)**2
    mu_max_y = b_y**2 * (Temp - Temp_min_y)**2
    return [
        mu_max_x * (x2/(x2 + 1)) * x1 * (1 - x1/xy_max - y1 / xy_max), # f1
        mu_max_x * x2,                                                 # f2
        mu_max_y * (y2/(y2 + 1)) * y1 * (1 - y1/xy_max - x1 / xy_max), # f3
        mu_max_y * y2,                                                 # f4
    ]

def ode_dfdp(t, x, u, p, ode_args):
    x1, x2, y1, y2 = x
    (Temp, ) = u
    (xy_max, b_x, Temp_min_x, b_y, Temp_min_y, ) = p
    # Define the maximum growth rate
    mu_max_x = b_x**2 * (Temp - Temp_min_x)**2
    mu_max_y = b_y**2 * (Temp - Temp_min_y)**2
    return [
        [
            mu_max_x * (x2/(x2 + 1)) * x1 * (x1 + y1) / (xy_max**2),                         # df1/dxy_max
             2 * b_x * (Temp - Temp_min_x)**2 * (x2/(x2 + 1)) * x1 * (1 - (x1 + y1)/xy_max), # df1/db_x
            -2 * b_x**2 * (Temp - Temp_min_x) * (x2/(x2 + 1)) * x1 * (1 - (x1 + y1)/xy_max), # df1/dTemp_min_x
            0,                                                                               # df1/db_y
            0                                                                                # df1/dTemp_min_y
        ],
        [
            0,                                      # df2/dxy_max
            2 * b_x * (Temp - Temp_min_x)**2 * x2,  # df2/dbx
            -2 * b_x**2 * (Temp - Temp_min_x) * x2, # df2/dTemp_minx
            0,
            0
        ],
        [
            mu_max_y * (y2/(y2 + 1)) * y1 * (x1 + y1) / (xy_max**2), # df3/dxy_max
            0,  
            0, 
            2 * b_y * (Temp - Temp_min_y)**2 * (y2/(y2 + 1)) * y1 * (1 - (x1 + y1)/xy_max),                      
            -2 * b_y**2 * (Temp - Temp_min_y) * (y2/(y2 + 1)) * y1 * (1 - (x1 + y1)/xy_max),                                                          
        ],
        [
            0, 
            0,
            0,                                               
            2 * b_y * (Temp - Temp_min_y)**2 * y2,                  
            -2 * b_y**2 * (Temp - Temp_min_y) * y2,                  
        ]
    ]

def ode_dfdx(t, x, u, p, ode_args):
    x1, x2, y1, y2 = x
    (Temp, ) = u
    (xy_max, b_x, Temp_min_x, b_y, Temp_min_y, ) = p
    # Define the maximum growth rate
    mu_max_x = b_x**2 * (Temp - Temp_min_x)**2
    mu_max_y = b_y**2 * (Temp - Temp_min_y)**2
    return [
        [
            mu_max_x * (x2/(x2 + 1)) * (1 - (2*x1 + y1)/xy_max),  # df1/dx1
            mu_max_x * 1/(x2 + 1)**2 * (1 - (x1 + y1)/xy_max)*x1, # df1/dx2
            -mu_max_x * x1 / xy_max,                              # df1/dy1
            0,                                                    # df1/dy2
        ],
        [
            0,                                                    # df2/dx1
            mu_max_x,                                             # df2/dx2
            0,
            0
        ],
        [
            -mu_max_y * y1 / xy_max,                              # df3/dx1
            0,
            mu_max_y * (y2/(y2 + 1)) * (1 - (2*y1 + x1)/xy_max),  # df3/dy1
            mu_max_y * 1/(y2 + 1)**2 * (1 - (x1 + y1)/xy_max)*y1, # df3/dy2
        ],
        [
            0,                                                                    # df4/dx1
            0,                                                                    # df4/dx2
            0,
            mu_max_y
        ]
    ]


if __name__ == "__main__":
    # Define parameters and initial conditions
    p = (2e4, 0.03, -8., 0.04, -5.5) # (x_max, b, T_min)
    x0 = np.array([50, 1., 20, 1.])

    # Define interval and number of sampling points for times
    times = {"lb": 0.0, "ub": 100.0, "n": 2}
 
    # Define explicit temperature points
    inputs = [{"lb": 2.0, "ub": 12.0, "n": 2}]

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
        obs_fun=[0, 2],
        covariance={"abs": 1.5, "rel": 1.5}
    )

    fsr = find_optimal(
        fsm,
        relative_sensitivities=True,
        recombination=0.7,
        mutation=(0.1, 0.8),
        workers=-1,
        popsize=12,
        #maxiter=10,
        polish=False,
        #disp=False
    )

    print("rank S = ", np.linalg.matrix_rank(fsr.S))

    # Plot all ODE results with chosen time points
    # for different data points
    conditions = f"2species_rel_sensit_cont_{2}times_{2}temps"
    plot_all_solutions(fsr, outdir="out/baranyi_2species", additional_name=conditions, file_format="pdf")
    json_dump(fsr, f"out/baranyi_2species/baranyi_roberts_2species_ode_fisher_determinant_{conditions}.json")

    '''
    det = []
    n_times = np.linspace(1, 6, 6, dtype=int)
    for nt in n_times:
        times = {"lb": 0.0, "ub": 12.0, "n": nt}

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
            obs_fun=[0, 2],
            covariance={"abs": 0.3, "rel": 0.1}
        )

        fsr = find_optimal(
            fsm,
            relative_sensitivities=True,
            recombination=0.7,
            mutation=(0.1, 0.8),
            workers=-1,
            popsize=10,
            polish=False,
            disp=False
        )

        det.append(fsr.criterion)
        print(f"nt = {nt} rank S = {np.linalg.matrix_rank(fsr.S)}\n\n")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(n_times, det, s=160, alpha=0.8, color="#440154", label="Optimal Design")
    ax.set_yscale('log')
    ax.set_ylabel("Determinant", fontsize=16)
    ax.set_xlabel("Number of measured times", fontsize=16)
    ax.tick_params(axis="y", labelsize=14)
    ax.tick_params(axis="x", labelsize=14)
    ax.legend(fontsize=16, framealpha=0.0)
    fig.savefig("out/baranyi_2species/det_vs_ntimes.png", bbox_inches='tight')
    # Remove figure to free space
    plt.close(fig)
    '''