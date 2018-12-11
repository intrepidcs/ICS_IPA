{
	"SignalListForUseInTimeBasis": ["TransOutputSpeed"],
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
		"StartExpression": "(TransOutputSpeed > 80) and (TransOutputSpeed < 100)",
		"EndExpression": "(AccelPedalPosition < 50) or (TransOutputSpeed > 1000)"
	},{
		"Description": "TipOutUpshifts",
		"StartExpression": "(AccelPedalPosition < 40) and (EngineSpeed > 4000)",
		"EndExpression": "(EngineSpeed < 2000)"
	},{
		"Description": "EngineStateVariableChangeFrom9To10",
		"StartExpression": "(EngineStateVariable1 == 9) and (Prev__EngineStateVariable1 == 8)",
		"EndExpression": "(TimeFromExpStart > 2)"
	}]
}
