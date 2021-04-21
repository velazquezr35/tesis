# -*- coding: utf-8 -*-
"""
Created on Mon Mar 22 17:15:47 2021

@author: Ramon Velazquez
"""

import openturns as ot
import time

def analisis_23D(X,v,dim,scale,**kwargs):
    
    if "full_output" in kwargs:
        f_otp_status = kwargs.get("full_output")
        
    start = time.time()

    X = ot.Sample(X)
    v = ot.Sample(v)

    basis = ot.QuadraticBasisFactory(dim).build()
    covarianceModel = ot.SquaredExponential([scale])
    algo = ot.KrigingAlgorithm(X,v,covarianceModel,basis)
    algo.run()
    result = algo.getResult()
    KM = result.getMetaModel()
    end = time.time()
    dt = end-start
    
    if f_otp_status:
        print("Sample X")
        print(X)
        print(" - - - - - - - - - - - -")
        print("Sample v")
        print(v)
        print(" - - - - - - - - - - - -")
        print("Tiempo requerido: "+ str(dt))
        print("Dimensión: " + str(dim))
        print("Size de sample input: " + str(len(X)))
    
    return(KM,dt)