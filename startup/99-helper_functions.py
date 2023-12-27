print(f"Loading {__file__}...")

## just adding functions we keep in defs.py so we don't need to keep dragging them around.  
##TODO evaluate ones for csxtools (because also good for db)
##TODO find better place inside of csx dir for these.


## Utility commands typically in startup.py..
bec.disable_baseline()

## Useful shorthands
ct = count
mv = bps.mv
mvr = bps.mvr
aset = bps.abs_set
rset = bps.rel_set
rsc = rel_scan
nap = bps.sleep


## Temporary fix due to faulty olog.. now not necessary anymore
#def olog_patch(string_to_write):
#    try:
#        olog(string_to_write)
#    except:
#        pass


def ct_dark_all_patch(frames=None):
    yield from mv(inout, "In")
    yield from mv(diag6_pid.enable, 0)
    yield from ct_dark_all(frames)
    yield from mv(inout, "Out")
    yield from mv(diag6_pid.enable, 1)
    yield from bps.sleep(.1)


def pol_L(pol, epu_cal_offset=None, epu_table_number=None):
    

    current_E = pgm.energy.setpoint.get()

    if epu_table_number is None:
        if pol == "H":
            epu_table_number = 5
        elif pol == "V":
            epu_table_number = 6
    
    yield from bps.mv(diag6_pid.enable,0) # OFF epu_table & m1a feedback
    if epu_cal_offset is not None:
        yield from bps.mv(epu2.flt.input_offset, epu_cal_offset)#, diag6_pid.setpoint, pid_setpoint) #update calibrations
        
    if pol == 'H':
        print(f'\n\n\tChanging phase to linear horizontal at THIS energy - {current_E:.2f}eV')
        yield from bps.mv(epu2.table, epu_table_number)
        yield from bps.mv(epu2.phase,0)
    elif pol == 'V':
        print(f'\n\n\tChanging phase to linear vertical at THIS energy - {current_E:.2f}eV')
        yield from bps.mv(epu2.table, epu_table_number)
        yield from bps.mv(epu2.phase,24.6)
    
    
    yield from bps.mv(diag6_pid.enable,1) # finepitch feedback ON
    yield from bps.sleep(1)

def pol_C(pol, epu_cal_offset=-267, epu_phase=None):
    '''This circular polarization change uses the horizontal polarization table and will force this table.  
    The offset is a best guess.  You should check the values to be certain.
    
    Fe L3
    Cpos = phase = 16.35 
    Cneg = phase = -16.46 -> -16.50 @ 20210806
    '''
    
    if pol == 'pos' or pol == 'neg':
        current_E = pgm.energy.setpoint.get()

        if pol == 'pos' and epu_phase is None:
            epu_phase = 16.35
        elif pol == 'neg' and epu_phase is None:
            epu_phase = -16.46
        
        yield from bps.mv(diag6_pid.enable,0) # OFF epu_table & m1a feedback
        yield from bps.mv(epu2.table, 2)  # forces use of LH polarization table
        yield from bps.mv(epu2.flt.input_offset, epu_cal_offset)
        #TODO add verbose stuff if claudio agrees
        #if pol == 'pos':
        #    print(f'\n\n\tChanging phase to C+ or pos at THIS energy - {current_E:.2f}eV')
        #    
        #    yield from bps.mv(epu2.phase,16.35)
        #elif pol == 'neg':
        #    print(f'\n\n\tChanging phase to C- or neg at THIS energy - {current_E:.2f}eV')
            
        yield from bps.mv(epu2.phase, epu_phase)
        
        yield from bps.mv(diag6_pid.enable,1) # finepitch feedback ON
        yield from bps.sleep(1)
    else:
        print('Allowed arguments for circular polarization are "neg" or "pos"')
        raise


def md_info(default_md = RE.md):
    '''Formatted print of RunEngine metadata or a scan_id start document
    Default behavior prints RE.md.'''


    print('Current default metadata for each scan are:')
    #print(len(default_md))
    for info in default_md:
        val = default_md[info]
        
        #print(info, val)
        print(f'    {info:_<30} : {val}')
    print('\n\n Use \'md_info()\' or \'RE.md\' to inspect again.')

def mvslt3(size=None): #TODO make a better version for slt3.pinhole child
    #x Mtr.OFF = 4.88, y Mtr.OFF = -0.95
    holes = {2000: ( -8.79, 0.00),    #TODO eventually have IOC to track these values
               50: (  0.00, 0.00),
               20: (  8.799, 0.065),
               10: ( 17.50,-0.045),} 
    if size is None:
        xpos = np.round( slt3.x.read()['slt3_x']['value'], 2)
        ypos = np.round( slt3.y.read()['slt3_y']['value'], 2)
        
        #for h in holes:  #TODO - now reverse lookup so the motion part is better
        #    #print('checking', xpos, ypos ,'for ', h[1])
        #    if xpos == h[1] and ypos == h[2]:
        #        print(f'{h[0]} um pinhole at slt3')
        #        break
            
    elif size is None:
        print(f'Unknown configuration: slt3.x = {xpos:.4f}, slt3.y = {ypos:.4f}') 


    else:
        print('Moving to {} um slit 3'.format(size))
        x_pos, y_pos = holes[size]
        yield from bps.mv(slt3.x, x_pos, slt3.y, y_pos)


# clear_suspenders can be triggered from the CLI using
#     $ qserver function execute '{"name":"clear_suspenders"}'
# or the equivalent function_execute API call
def clear_suspenders():
    print('clear_suspenders called')
    RE.clear_suspenders()
