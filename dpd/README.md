# DPD Implementation

Original JSON are from: https://github.com/digitalpalidictionary/dpd-db/tree/feature/db-relations/tbw/output

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

## Transorm file into simple dictinonary

via the `dpd-format-script.js` we create simple dictionnaries and store them in the dictinaries folder -> simple.

Careful, these files have the same name, but are not identical.