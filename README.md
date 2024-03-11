# kindergarten2osm
Load kindergartens from Barnehagefakta api and produce OSM file. 

### Usage ###

<code>python kindergarten2osm.py [-noadjust]</code>

Usage:
* <code>-noadjust</code>: Do not adjust coordinates to middle of building.

### Notes ###

* This program extracts kindergartens from the National Kindergarten Registry/Norsk Barnehageregister (NBR) by the Norwegian Directorate for Education and Training, and produces an OSM file with all kindergartens; approx. 6000 public and private kindergartens for the whole country of Norway.
* NBR is collecting data from the [Central Register of Establishments and Enterprises](https://ssb.no/a/metadata/om_datasamlinger/virksomhets-_og_foretaksregisteret/bof.html) as well as from other sources, such as [Basil](https://basil.udir.no/). Data quality ultimatly depends on input from each kindergarten.
  * Coordinates without a proper address (street + house number) may be missing. Run [geocode2osm](https://github.com/NKAmapper/geocode2osm) for those to get at least the street or post district.
  * Kidergartens which have been set as inactive in Basil may not be in operation. You may want to consult indexed search engines to discover their status.
  * A few kindergartens are in fact just administrative offices or service functions and should not be imported to OSM.
* Coordinates will be centered on the underlying building if inside a building.
* The directorate recommends extrating data outside of normal business hours to get a consistent data set.
* Use [update2osm](https://github.com/osmno/update2osm) to discover differences with regards to schools currently in OSM, and to get an OSM file ready for inspection and uploading, based on the _ref:barnehage_ tag.

### References ###

* [Barnehagefakta](https://www.barnehagefakta.no)
* [Utdanningsdirektoratet - NSR](https://nsr.udir.no).
* [Utdanningsdirektoratet - Open data](https://www.udir.no/om-udir/data).
* [API for barnehager](https://data-nbr.udir.no/swagger/index.html).
* [Basil - Innrapportering for barnehager](https://basil.udir.no/)
* [Virksomhets- og foretaksregisteret (VoF)](https://ssb.no/a/metadata/om_datasamlinger/virksomhets-_og_foretaksregisteret/bof.html).
