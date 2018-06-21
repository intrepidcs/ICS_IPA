{
	"_commentChannels": "The Channels shown below are a list of channels used for opening and searching through data files",
	"Channels": [{
		"name_in_script": "TransOutputSpeed",
		"OptionalList": [{
			"channel_name": "TransOutputSpeed",
			"message_name": "Group0011",
			"network_name": ""
		}]
	}, {
		"name_in_script": "TransTurbineSpeed",
		"OptionalList": [{
			"channel_name": "TransTurbineSpeed",
			"message_name": "Group0012",
			"network_name": ""
		}]
	}, {
		"name_in_script": "EngineSpeed",
		"OptionalList": [{
			"channel_name": "EngineSpeed",
			"message_name": "Group0013",
			"network_name": ""
		}]
	}, {
		"name_in_script": "AccelPedalPosition",
		"OptionalList": [{
			"channel_name": "AccelPedalPosition",
			"message_name": "Group0020",
			"network_name": ""
		}]
	}, {
		"name_in_script": "EngineStateVariable1",
		"OptionalList": [{
			"channel_name": "EngineStateVariable1",
			"message_name": "Group0010",
			"network_name": ""
		}]
	}],
	"EventDefinitions": [{
		"Description": "WOTLaunchFromRest",
		"StartExpression": "(AccelPedalPosition > 80) and (TransOutputSpeed < 100)",
		"EndExpression": "(AccelPedalPosition < 50) or (TransOutputSpeed > 1000)"
	},{
		"Description": "TipOutUpshifts",
		"StartExpression": "(AccelPedalPosition < 40) and (EngineSpeed > 4000)",
		"EndExpression": "(EngineSpeed < 2000)"
	},{
		"Description": "EngineStateVariableChangeFrom9To10",
		"StartExpression": "(EngineStateVariable1 == 9) and (Prev__EngineStateVariable1 == 8)",
		"EndExpression": "(TimeFromExpStart > 2)"
	}],
	"_commentOutputChannels": "The OutputChannels shown below are a list of channels that you want to include in the mdf output file",
	"OutputChannels": [{
		"name_in_script": "TransmissionEff",
		"OptionalList": [{
			"channel_name": "TransmissionEff",
			"message_name": "Group0001",
			"network_name": ""
		}]
	}, {
		"name_in_script": "EnginePower",
		"OptionalList": [{
			"channel_name": "EnginePower",
			"message_name": "Group0002",
			"network_name": ""
		}]
	}, {
		"name_in_script": "KnockSensorMag",
		"OptionalList": [{
			"channel_name": "KnockSensorMag",
			"message_name": "Group0003",
			"network_name": ""
		}]
	}, {
		"name_in_script": "O2_DownstreamTrim1",
		"OptionalList": [{
			"channel_name": "O2_DownstreamTrim1",
			"message_name": "Group0004",
			"network_name": ""
		}]
	}, {
		"name_in_script": "PurgeFlow",
		"OptionalList": [{
			"channel_name": "PurgeFlow",
			"message_name": "Group0005",
			"network_name": ""
		}]
	}, {
		"name_in_script": "O2SensorTrimFactor",
		"OptionalList": [{
			"channel_name": "O2SensorTrimFactor",
			"message_name": "Group0006",
			"network_name": ""
		}]
	}, {
		"name_in_script": "ExhValvePosition",
		"OptionalList": [{
			"channel_name": "ExhValvePosition",
			"message_name": "Group0007",
			"network_name": ""
		}]
	}, {
		"name_in_script": "IntakeValvePosition",
		"OptionalList": [{
			"channel_name": "IntakeValvePosition",
			"message_name": "Group0008",
			"network_name": ""
		}]
	}, {
		"name_in_script": "EGRValvePos",
		"OptionalList": [{
			"channel_name": "EGRValvePos",
			"message_name": "Group0009",
			"network_name": ""
		}]
	}, {
		"name_in_script": "AccessVolt_LowVoltage",
		"OptionalList": [{
			"channel_name": "AccessVolt_LowVoltage",
			"message_name": "Group0010",
			"network_name": ""
		}]
	}, {
		"name_in_script": "EngineStateVariable1",
		"OptionalList": [{
			"channel_name": "EngineStateVariable1",
			"message_name": "Group0010",
			"network_name": ""
		}]
	}, {
		"name_in_script": "IntakeManifoldPressure",
		"OptionalList": [{
			"channel_name": "IntakeManifoldPressure",
			"message_name": "Group0010",
			"network_name": ""
		}]
	}, {
		"name_in_script": "VehSpeed",
		"OptionalList": [{
			"channel_name": "VehSpeed",
			"message_name": "Group0010",
			"network_name": ""
		}]
	}, {
		"name_in_script": "TransOutputSpeed",
		"OptionalList": [{
			"channel_name": "TransOutputSpeed",
			"message_name": "Group0011",
			"network_name": ""
		}]
	}, {
		"name_in_script": "TransTurbineSpeed",
		"OptionalList": [{
			"channel_name": "TransTurbineSpeed",
			"message_name": "Group0012",
			"network_name": ""
		}]
	}, {
		"name_in_script": "EngineSpeed",
		"OptionalList": [{
			"channel_name": "EngineSpeed",
			"message_name": "Group0013",
			"network_name": ""
		}]
	}, {
		"name_in_script": "IntakeAirTemp",
		"OptionalList": [{
			"channel_name": "IntakeAirTemp",
			"message_name": "Group0014",
			"network_name": ""
		}]
	}, {
		"name_in_script": "SpkAdvance",
		"OptionalList": [{
			"channel_name": "SpkAdvance",
			"message_name": "Group0015",
			"network_name": ""
		}]
	}, {
		"name_in_script": "ExhTemp",
		"OptionalList": [{
			"channel_name": "ExhTemp",
			"message_name": "Group0016",
			"network_name": ""
		}]
	}, {
		"name_in_script": "CatalystTemp",
		"OptionalList": [{
			"channel_name": "CatalystTemp",
			"message_name": "Group0017",
			"network_name": ""
		}]
	}, {
		"name_in_script": "TargetIdleSpeed_DR",
		"OptionalList": [{
			"channel_name": "TargetIdleSpeed_DR",
			"message_name": "Group0018",
			"network_name": ""
		}]
	}, {
		"name_in_script": "TargetIdleSpeed_PN",
		"OptionalList": [{
			"channel_name": "TargetIdleSpeed_PN",
			"message_name": "Group0019",
			"network_name": ""
		}]
	}, {
		"name_in_script": "AccelPedalPosition",
		"OptionalList": [{
			"channel_name": "AccelPedalPosition",
			"message_name": "Group0020",
			"network_name": ""
		}]
	}, {
		"name_in_script": "OutputSpeedAccel",
		"OptionalList": [{
			"channel_name": "OutputSpeedAccel",
			"message_name": "Group0021",
			"network_name": ""
		}]
	}, {
		"name_in_script": "EngineTorqReq",
		"OptionalList": [{
			"channel_name": "EngineTorqReq",
			"message_name": "Group0022",
			"network_name": ""
		}]
	}, {
		"name_in_script": "EngineTorqRaw",
		"OptionalList": [{
			"channel_name": "EngineTorqRaw",
			"message_name": "Group0023",
			"network_name": ""
		}]
	}, {
		"name_in_script": "EngineTorqMin_WithoutAccess",
		"OptionalList": [{
			"channel_name": "EngineTorqMin_WithoutAccess",
			"message_name": "Group0024",
			"network_name": ""
		}]
	}, {
		"name_in_script": "EngineTorqMin_LimpHome",
		"OptionalList": [{
			"channel_name": "EngineTorqMin_LimpHome",
			"message_name": "Group0025",
			"network_name": ""
		}]
	}, {
		"name_in_script": "EngineTorqMin_Curr",
		"OptionalList": [{
			"channel_name": "EngineTorqMin_Curr",
			"message_name": "Group0026",
			"network_name": ""
		}]
	}, {
		"name_in_script": "EngineTorqMax_WithoutAccess",
		"OptionalList": [{
			"channel_name": "EngineTorqMax_WithoutAccess",
			"message_name": "Group0027",
			"network_name": ""
		}]
	}, {
		"name_in_script": "EngineTorqMax_SlowPath",
		"OptionalList": [{
			"channel_name": "EngineTorqMax_SlowPath",
			"message_name": "Group0028",
			"network_name": ""
		}]
	}, {
		"name_in_script": "EngineTorqMax_LimpHome",
		"OptionalList": [{
			"channel_name": "EngineTorqMax_LimpHome",
			"message_name": "Group0029",
			"network_name": ""
		}]
	}, {
		"name_in_script": "EngineTorqMax_FastPath",
		"OptionalList": [{
			"channel_name": "EngineTorqMax_FastPath",
			"message_name": "Group0030",
			"network_name": ""
		}]
	}, {
		"name_in_script": "EngineTorqMax_Cur",
		"OptionalList": [{
			"channel_name": "EngineTorqMax_Cur",
			"message_name": "Group0031",
			"network_name": ""
		}]
	}, {
		"name_in_script": "EngineTorq_ReqNet",
		"OptionalList": [{
			"channel_name": "EngineTorq_ReqNet",
			"message_name": "Group0032",
			"network_name": ""
		}]
	}, {
		"name_in_script": "EngineSpeedTargetAccel",
		"OptionalList": [{
			"channel_name": "EngineSpeedTargetAccel",
			"message_name": "Group0033",
			"network_name": ""
		}]
	}, {
		"name_in_script": "BatMinTemp",
		"OptionalList": [{
			"channel_name": "BatMinTemp",
			"message_name": "Group0034",
			"network_name": ""
		}]
	}, {
		"name_in_script": "EngineCoolantTemp",
		"OptionalList": [{
			"channel_name": "EngineCoolantTemp",
			"message_name": "Group0034",
			"network_name": ""
		}]
	}, {
		"name_in_script": "BatMaxTemp",
		"OptionalList": [{
			"channel_name": "BatMaxTemp",
			"message_name": "Group0034",
			"network_name": ""
		}]
	}, {
		"name_in_script": "BatTempActual",
		"OptionalList": [{
			"channel_name": "BatTempActual",
			"message_name": "Group0034",
			"network_name": ""
		}]
	}, {
		"name_in_script": "EngineStateVariable5",
		"OptionalList": [{
			"channel_name": "EngineStateVariable5",
			"message_name": "Group0035",
			"network_name": ""
		}]
	}, {
		"name_in_script": "TorqueConverterSpeedRatio",
		"OptionalList": [{
			"channel_name": "TorqueConverterSpeedRatio",
			"message_name": "Group0035",
			"network_name": ""
		}]
	}, {
		"name_in_script": "TorqConv_Pressure",
		"OptionalList": [{
			"channel_name": "TorqConv_Pressure",
			"message_name": "Group0036",
			"network_name": ""
		}]
	}, {
		"name_in_script": "EngineStateVariable3",
		"OptionalList": [{
			"channel_name": "EngineStateVariable3",
			"message_name": "Group0037",
			"network_name": ""
		}]
	}, {
		"name_in_script": "EngineStateVariable7",
		"OptionalList": [{
			"channel_name": "EngineStateVariable7",
			"message_name": "Group0037",
			"network_name": ""
		}]
	}, {
		"name_in_script": "AccessVolt_Actual",
		"OptionalList": [{
			"channel_name": "AccessVolt_Actual",
			"message_name": "Group0038",
			"network_name": ""
		}]
	}, {
		"name_in_script": "BrakePedalPosition",
		"OptionalList": [{
			"channel_name": "BrakePedalPosition",
			"message_name": "Group0038",
			"network_name": ""
		}]
	}, {
		"name_in_script": "EngineStateVariable4",
		"OptionalList": [{
			"channel_name": "EngineStateVariable4",
			"message_name": "Group0038",
			"network_name": ""
		}]
	}, {
		"name_in_script": "EngineStateVariable6",
		"OptionalList": [{
			"channel_name": "EngineStateVariable6",
			"message_name": "Group0038",
			"network_name": ""
		}]
	}, {
		"name_in_script": "AccessVolt_Setpoint",
		"OptionalList": [{
			"channel_name": "AccessVolt_Setpoint",
			"message_name": "Group0039",
			"network_name": ""
		}]
	}]
}
