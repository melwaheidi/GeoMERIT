Dr. Mahmoud M. Elwaheidi
Department of Geology and Geophysics, College of Science
King Saud University, Riyadh 11451, Saudi Arabia
melwaheidi@ksu.edu.sa | ORCID 0000-0003-4863-3184

To the Editors, Applied Computing and Geosciences

Dear Editors,

I am pleased to submit the manuscript "GeoMERIT: an open-source tool for
reproducible target-specific selection of near-surface geophysical methods"
for consideration as a software or tools article.

Choosing an appropriate geophysical method for a near-surface investigation is
a routine but consequential decision that is usually made by tacit expert
judgement, and is therefore inconsistent across practitioners and difficult to
document or reproduce. The manuscript presents GeoMERIT, an open-source Python
tool that makes this decision systematic and transparent. It ranks nine common
near-surface methods for a stated investigation target using a weighted sum
over an explicit, literature-derived method-by-target physical-property-contrast
matrix, so that recommendations are conditioned on the physics of the specific
target and every element of a recommendation can be inspected and modified. The
tool is released under the MIT License, archived with a citable DOI, and
accompanied by scripts that regenerate every reported result, table, and figure
from documented parameters.

GeoMERIT is evaluated against documented field practice without recourse to
human subjects. In a retrospective test at three documented coastal-aquifer and
landfill sites the top-ranked method matches the deployed method at two of
three, and in a reproducible benchmark of 22 documented literature cases
spanning groundwater, void, and archaeological targets the deployed method is
ranked first in 45.5% of cases and appears within the top-three shortlist in
81.8%. The agreement is stable to parameter encoding and to the choice of
criterion weights, and a target-aware formulation outperforms a target-blind
control. The same benchmark also reveals, and the manuscript reports plainly, a
structural limitation at first place, which a failure-mode analysis attributes
to specific parts of the knowledge base; the reproducible benchmark and its
auditing scripts thus constitute a secondary contribution, namely a transparent
method for evaluating method-selection aids against real field practice.

The manuscript is original, is not under consideration elsewhere, and has a
single author. The source code, the machine-readable benchmark, and the
reproduction scripts are openly available on GitHub and archived at Zenodo, as
detailed in the data-availability statement. There are no competing interests.

Thank you for considering this submission.

Yours sincerely,

Mahmoud M. Elwaheidi
