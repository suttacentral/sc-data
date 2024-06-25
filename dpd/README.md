# DPD Implementation

See https://github.com/digitalpalidictionary/dpd-db/tree/feature/db-relations/tbw for explaination

## Lookup Word Description

This dictinonary relies on 3 different files:

    BEHAVIOUR
    take the word variable and search for that in dpd_i2h.json
    	if it return a list of headwords
    		look up each headword in the list in dpd_ebts.json
    			add the result to html string
    lookup the word in  dpd_deconstructor.json
    	if it returns any results
    		 add the result to html string
    display the html string

## Transorm files into simple dictinonary

Via the `dpd-format-script.js` we create 3 simple dictionnaries. But might be inconveniant.

## Make Unique Master Dictionary

Via `dpd-master-script.js` you can create one master simple dictionnary.