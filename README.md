# Directories
## Parameters
### Transitions times files
Contains the random draws of **transitions times** for the synthetic use-case. Located in ```parameters/transitions_times```.\
The file name describes the content, i.e.:
```transitions_times-<min_duration>-<max_duration>-deps<nb_deps>-<draw_number>.json```
For the ICSOC, 2 draws 0 and 1 have been generated.

### Transitions time generation
The **random generation** of the transitions times is done in the file ```transitions_times_generation.py```. The parameters of the generation
are put directly in the file, and the distribution follows a **lognormal distribution**.

### Uptimes files
Contains the pseudo-random generated uptimes for the synthetic use case. Located in ```parameters/uptimes```.\
The file name describes the content, i.e.:
```uptimes-<nb_uptimes>-<duration>-<nb_deps>-<min_overlap>-<max_overlap>.json```
For the ICSOC, 4 uptimes corresponding to 4 overlap rates have been generated: 2-5% (0_02-0_05), 20-30% (0_2-0_3),
50-60% (0_5-0_6), 100% (1-1).

### Uptimes pseudo-random generation
In all these scripts, the term **dependency** is used for all dependencies **and for the server (which is the 0th dep)**.

The script ```uptimes/uptimes_generation_overview.py``` gives a graphic overview of an uptime generation for a given overlap. But
the resulted scripts are not used for the experiment. It is only to preview the aspect of the different possibles overlaps rates.

The script that pseudo-random generate uptimes that are used for the experiment is ```uptimes/uptimes_generation_logic.py```.\
To use it:
- Change the **parameters** inside the script (round: total nb of times to wake up, duration: duration of a wake up, nb_deps: total number of **deps only**,
the server is **considered implicit and is always here**, overlap_taux: overlap rate, nb_generations: how many generation do you want)
- Call the script with *generate*: ```python3 uptimes_generation_logic.py generate```. It will generate as many files as <nb_generations>.
These files contain the desired overlaps duration for each dependency, for each round.
- Call the script with *see*: ```python3 uptimes_generation_logic.py see <file_name>```. To have informations about a generated file.
- Call the script with *compute*: ```python3 uptimes_generation_logic.py compute <file_name>```. It will compute the actual uptimes for each dependency and for 
the server, by respecting the desired overlap rate for dependency and for each round. The desired overlap rate is written in on of the previously generated files, reference by <file_name>.

## Results
The ```raw_results``` folder contains all the results of the experiment that was conducted for the ICSOC 2022. These results
are not ordered.

The ```global_results_4_draws.json``` are the result of the execution of the script ```compute_globals_results.py``` on ```raw_results```. 
In order to have the same amount of draws for every results, draws in excess are removed from the results (some results 
have 5 to 8 draws). However, removing these draws do not have a significant impact on the resulting std.

In order to get the full results, run the script ```python3 compute_globals_results.py```.
