# INIT FUNCTION
def hex2bin(HexInputStr, outFormat=4):
    '''This function accepts the following two args.
    1) A Hex number as input string and
    2) Optional int value that selects the desired Output format(int value 8 for byte and 4 for nibble [default])
    The function returns binary equivalent value on the first arg.'''
    int_value = 0
    output_length = 0
    try :
        int_value = int(HexInputStr, 16)
        if(outFormat == 8):
            output_length = 8 * ((len(HexInputStr) + 1 ) // 2) # Byte length output i.e input A is printed as 00001010
        else:
            output_length = (len(HexInputStr)) * 4 # Nibble length output i.e input A is printed as 1010
    except Exception as e :
        print(e)

    bin_value = f'{int_value:0{output_length}b}' # new style
    return bin_value

def hex2dec(s):
    try :
        return int(s, 16)
    except Exception as e :
        return 0

def bin2dec(BinaryInputStr): 
    try :
        return int(BinaryInputStr,2)
    except Exception as e :
        return 0 

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]

def simplex_parser(current_payload,before_payload):
    # init setter
    PAYLOAD = current_payload
    BEFORE_PAYLOAD = before_payload
    RESULT = {}

    # remove 0x hex
    payload = PAYLOAD.lstrip('0x')  

    # =MID(C2,3,6)
    mid_a = payload[2:8]

    # =MID(C2,9,6)
    mid_b = payload[8:14]

    # =SUM(90/POWER(2,23))
    power_90 = 90/(2**23)

    # =SUM(180/POWER(2,23))
    power_180 = 180/(2**23)

    # Format text excell
    #print("{:.10f}".format(power_90));

    # =IF(SUM($A$3*(HEX2DEC(D2)))>90,SUM($A$3*(HEX2DEC(D2)))-180,SUM($A$3*(HEX2DEC(D2))))
    latitude = power_90 * int(mid_a, 16)
    if ( latitude > 90 ):
        latitude = latitude - 180
        RESULT['latitude'] = latitude
    else :
        RESULT['latitude'] = latitude

    # =IF(SUM($A$4*HEX2DEC(E2))>180,SUM($A$4*HEX2DEC(E2))-360,SUM($A$4*HEX2DEC(E2)))
    longitude = power_180 * int(mid_b, 16)
    if ( longitude > 180 ):
        longitude = longitude - 360
        RESULT['longitude'] = longitude
    else :
        RESULT['longitude'] = longitude

    """
    # Message Type
    0	Normal Location
    1	Unit Turned On
    2	Change of Location
    3	Contact State Change
    4	Contact Not Normal
    5	Re-center
    """
    # Message Types'!$A$3:$B$8
    # Type 0 Messages
    MESSAGE_TYPE_0 = {}
    MESSAGE_TYPE_0[0]="Normal Location"
    MESSAGE_TYPE_0[1]="Unit Turned on"
    MESSAGE_TYPE_0[2]="Change of Location"
    MESSAGE_TYPE_0[3]="Contact State Change"
    MESSAGE_TYPE_0[4]="Contact Not Normal"
    MESSAGE_TYPE_0[5]="Re-center"

    MESSAGE_TYPE_3 = {}
    MESSAGE_TYPE_3[21]="Statistics"
    MESSAGE_TYPE_3[22]="Replace Battery"
    MESSAGE_TYPE_3[23]="Contact Service Provider"
    MESSAGE_TYPE_3[24]="Accumulate/Count"

    # =BIN2DEC(RIGHT(HEX2BIN(MID($B9,4,1)),2))
    # J15
    msg_type_1 = bin2dec(right(hex2bin(mid(PAYLOAD,3,1),8),2))
    RESULT['msg_type_1'] = msg_type_1
    #print("Message type I : %s" % msg_type_1)

    # =IF(J15=0,"-",BIN2DEC(LEFT(HEX2BIN(MID($B15,3,2),8),6)))
    # K15
    subtype = "-"
    if(msg_type_1 > 0):
        subtype = bin2dec(left(hex2bin(mid(PAYLOAD,2,2),8),6))
    #print("Sub type : %s" % subtype)
    RESULT['subtype'] = subtype

    # =HEX2DEC(MID(B9,17,1))
    # L15
    msg_type_2 = int(mid(PAYLOAD, 16, 1), 16)
    RESULT['msg_type_2'] = msg_type_2
    #print("Message type II : %s" % msg_type_2)

    # =IF(J2=0,VLOOKUP(L2,'Message Types'!$A$3:$B$8,2,FALSE),VLOOKUP(K2,'Message Types'!$D$3:$E$6,2,FALSE))
    # DESCRIPTION MESSAGE TYPE
    # I15
    message_data = ""
    if(msg_type_1 == 0):
        message_data = MESSAGE_TYPE_0[msg_type_2]
    else :
        message_data = MESSAGE_TYPE_3[subtype]
    RESULT['message_type'] = message_data
    #print("Messsage type : %s" % message_data)

    # =MID($B14,20,1)
    # UMN M15
    umn = mid(PAYLOAD,19,1)
    RESULT['umn'] = umn
    #print("UMN : %s" % umn)

    # =IF(J14=0,MID(HEX2BIN(MID(B14,3,2),8),6,1),IF(K14=24,MID(HEX2BIN(MID(B13,5,2),8),4,1),"-"))
    # BATTERY N15
    if(msg_type_1 == 0):
        #MID(HEX2BIN(MID(B14,3,2),8),6,1)
        #print(mid(hex2bin(mid(PAYLOAD,2,2),8)),5,1)
        battery = mid(hex2bin(mid(PAYLOAD,2,2),8),5,1)
    else :
        if (subtype == 24):
            battery = mid(hex2bin(mid(BEFORE_PAYLOAD,4,2),8),3,1)
        else :
            battery = "-"
    #print("Battery : %s" % battery)
    RESULT['battery'] = battery

    # GPS VALID
    # =MID(HEX2BIN(MID($B15,3,2),8),5,1)
    gps_valid = mid(hex2bin(mid(PAYLOAD,2,2),8),4,1)
    RESULT['gps_valid'] = gps_valid
    #print("GPS Valid : %s" % gps_valid)

    # MISSED CONTACT 1
    # =MID(HEX2BIN(MID($B15,3,2),8),4,1)
    miss_contact_1 = mid(hex2bin(mid(PAYLOAD,2,2),8),3,1)
    RESULT['miss_contact_1'] = miss_contact_1
    #print("Missed contact 1 : %s" % miss_contact_1)

    # MISSED CONTACT 2
    # =MID(HEX2BIN(MID($B15,3,2),8),3,1)
    miss_contact_2 = mid(hex2bin(mid(PAYLOAD,2,2),8),2,1)
    RESULT['miss_contact_2'] = miss_contact_2
    #print("Missed contact 2 : %s" % miss_contact_2)

    # GPS FAIL COUNT
    # =BIN2DEC(MID(HEX2BIN(MID($B15,3,2),8),1,2))
    gps_fail_count = bin2dec(mid(hex2bin(mid(PAYLOAD,2,2),8),0,2))
    RESULT['gps_fail_count'] = gps_fail_count
    #print("GPS Fail count : %s" % gps_fail_count)

    # Battery Contact Status
    # =HEX2BIN(MID($B15,18,1),4)
    battery_contact_status = hex2bin(mid(PAYLOAD,17,1),4)
    RESULT['battery_contact_status'] = battery_contact_status
    #print("Battery contact status : %s" % battery_contact_status)

    # MOTION
    # =MID(HEX2BIN(MID($B15,19,2),8),2,1)
    motion = mid(hex2bin(mid(PAYLOAD,18,2),8),1,1)
    RESULT['motion'] = motion
    #print("Motion : %s" % motion)

    # FIX CONFIDENCE
    # =MID(HEX2BIN(MID($B15,19,2),8),1,1)
    fix_confidence = mid(hex2bin(mid(PAYLOAD,18,2),8),0,1)
    RESULT['fix_confidence'] = fix_confidence
    #print("Fix confidence : %s" % fix_confidence)

    # TX PERBURST
    # =IF(AND($J15=3,$K15<>24),"numtx","-")
    tx_perburst = ""
    if ((msg_type_1 == 3) and (subtype != 15)):
        tx_perburst = "numtx"
    else :
        tx_perburst = "-"
    RESULT['tx_perburst'] = tx_perburst
    #print("TX perburst : %s" % tx_perburst)

    # GPS FAULT
    # =IF(AND($J15=3,$K15<>24),MID(HEX2BIN(MID($B15,5,1),4),3,1),"-")
    gps_fault = "-"
    if ((msg_type_1 == 3) and (subtype != 15)):
        gps_fault = mid(hex2bin(mid(PAYLOAD,4,1),4),2,1)
    RESULT['gps_fault'] = gps_fault
    #print("GPS Fault : %s" % gps_fault)

    # TRANSMITTER FAULT
    # =IF(AND($J15=3,$K15<>24),MID(HEX2BIN(MID($B15,5,1),4),3,1),"-")
    transmitter_fault = "-"
    if ((msg_type_1 == 3) and (subtype != 15)):
        transmitter_fault = mid(hex2bin(mid(PAYLOAD,4,1),4),2,1)
    RESULT['transmitter_fault'] = transmitter_fault
    #print("Transmitter Fault : %s" % transmitter_fault)

    # SCHEDULLER FAULT
    # =IF(AND($J15=3,$K15<>24),MID(HEX2BIN(MID($B15,5,1),4),3,1),"-")
    scheduller_fault = "-"
    if ((msg_type_1 == 3) and (subtype != 15)):
        scheduller_fault = mid(hex2bin(mid(PAYLOAD,4,1),4),2,1)
    RESULT['scheduller_fault'] = scheduller_fault
    #print("Scheduller Fault : %s" % scheduller_fault)

    # MIN INTERVAL
    # =IF(AND($J15=3,$K15<>24),MID(HEX2BIN(MID($B15,5,1),4),3,1),"-")
    min_interval = "-"
    if ((msg_type_1 == 3) and (subtype != 15)):
        min_interval = mid(hex2bin(mid(PAYLOAD,4,1),4),2,1)
    RESULT['min_interval'] = min_interval
    #print("Min interval : %s" % min_interval)

    # MAX INTERVAL
    # =IF(AND($J15=3,$K15<>24),MID(HEX2BIN(MID($B15,5,1),4),3,1),"-")
    max_interval = "-"
    if ((msg_type_1 == 3) and (subtype != 15)):
        max_interval = mid(hex2bin(mid(PAYLOAD,4,1),4),2,1)
    RESULT['max_interval'] = max_interval
    #print("Max interval : %s" % max_interval)

    # GPS MEAN SEARCH TIME
    # =IF(AND($J15=3,$K15<>24),MID(HEX2BIN(MID($B15,5,1),4),3,1),"-")
    gps_mean_search_time = "-"
    if ((msg_type_1 == 3) and (subtype != 15)):
        gps_mean_search_time = mid(hex2bin(mid(PAYLOAD,4,1),4),2,1)
    RESULT['gps_mean_search_time'] = gps_mean_search_time
    #print("GPS Mean Search Time : %s" % gps_mean_search_time)

    # GPS FAIL COUNT
    # =IF(AND($J15=3,$K15<>24),MID(HEX2BIN(MID($B15,5,1),4),3,1),"-")
    gps_fail_count_2 = "-"
    if ((msg_type_1 == 3) and (subtype != 15)):
        gps_fail_count_2 = mid(hex2bin(mid(PAYLOAD,4,1),4),2,1)
    RESULT['gps_fail_count_2'] = gps_fail_count_2
    #print("GPS Fail Count : %s" % gps_fail_count_2)

    # TRANSMISION COUNT
    # =IF(AND($J15=3,$K15<>24),MID(HEX2BIN(MID($B15,5,1),4),3,1),"-")
    transmition_count = "-"
    if ((msg_type_1 == 3) and (subtype != 15)):
        transmition_count = mid(hex2bin(mid(PAYLOAD,4,1),4),2,1)
    RESULT['transmition_count'] = transmition_count
    #print("Transmition Count : %s" % transmition_count)

    # ACCUMULATE CONTACT 1
    # =IF(AND($J15=3,$K15=24),HEX2DEC(MID($B15,5,4)),"-")
    accumulate_contact_1 = "-"
    if ((msg_type_1 == 3) and (subtype == 24)):
        accumulate_contact_1 = hex2dec(mid(PAYLOAD,4,4))
    RESULT['accumulate_contact_1'] = accumulate_contact_1
    #print("Accumulate contact 1 : %s" % accumulate_contact_1)

    # ACCUMULATE CONTACT 2
    # =IF(AND($J15=3,$K15=24),HEX2DEC(MID($B15,9,4)),"-")
    accumulate_contact_2 = "-"
    if ((msg_type_1 == 3) and (subtype == 24)):
        accumulate_contact_2 = hex2dec(mid(PAYLOAD,8,4))
    RESULT['accumulate_contact_2'] = accumulate_contact_2
    #print("Accumulate contact 2 : %s" % accumulate_contact_2)

    # ACCUMULATE VIBRATION
    # =IF(AND($J15=3,$K15=24),HEX2DEC(MID($B15,13,4)),"-")
    accumulate_vibration = "-"
    if ((msg_type_1 == 3) and (subtype == 24)):
        accumulate_vibration = hex2dec(mid(PAYLOAD,12,4))
    RESULT['accumulate_vibration'] = accumulate_vibration
    #print("Accumulate vibration : %s" % accumulate_vibration)

    # CONTACT 1 COUNT
    # =IF(AND($J15=3,$K15=24),HEX2DEC(MID($B15,17,2)),"-")
    contact_1_count = "-"
    if ((msg_type_1 == 3) and (subtype == 24)):
        contact_1_count = hex2dec(mid(PAYLOAD,16,2))
    RESULT['contact_1_count'] = contact_1_count
    #print("Contact 1 count : %s" % contact_1_count)

    # CONTACT 2 COUNT
    # =IF(AND($J15=3,$K15=24),HEX2DEC(MID($B15,19,2)),"-")
    contact_2_count = "-"
    if ((msg_type_1 == 3) and (subtype == 24)):
        contact_2_count = hex2dec(mid(PAYLOAD,18,2))
    RESULT['contact_2_count'] = contact_2_count
    #print("Contact 2 count : %s" % contact_2_count)

    return RESULT

if __name__== "__main__" :
    # parameter 1 adalah hex yang akan di parsing, sedangkan parameter ke dua adalah naik 1x keatas sebelum hex ini
    result = simplex_parser("0x40F6B4354C69810A00", "0x0028C004BA23131A20")
    print(result)
