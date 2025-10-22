# -*- coding: utf-8 -*-
"""
Created on Thu Jun 12 15:39:39 2025

@author: MA282944
"""

import configparser
config = configparser.ConfigParser()
config['DEFAULT'] = {'portImprimante' : 'COM7', 'portArduino' : 'COM5','baudrate' : '115200', 'pin_finDeCourse' : '7', 'pin_buzzer' : '2', 'pin_relaiCycleChauffe' : '4'}
config['Constante']={'Vitesse_deplacement': '3000', 'pos_x_min_depose_ec' : '96', 'pos_x_max_depose_ec' : '229', 'espacement_ec_depose_x' : '19', 'pos_y_min_depose_ec' : '35', 'pos_y_max_depose_ec' : '38.8', 'espacement_ec_depose_y' : '0.4', 'hauteur_secu_z' : '35', 'delta_z_posDesassemblage' : '4'}
with open('config.ini', 'w') as configfile:
    config.write(configfile)