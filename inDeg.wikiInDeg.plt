#
# wiki-vote In Degree. G(50, 97). 16 (0.3200) nodes with in-deg > avg deg (3.9), 4 (0.0800) with >2*avg.deg (Thu Aug 03 15:53:59 2017)
#

set title "wiki-vote In Degree. G(50, 97). 16 (0.3200) nodes with in-deg > avg deg (3.9), 4 (0.0800) with >2*avg.deg"
set key bottom right
set logscale xy 10
set format x "10^{%L}"
set mxtics 10
set format y "10^{%L}"
set mytics 10
set grid
set xlabel "In-degree"
set ylabel "Count"
set tics scale 2
set terminal png font arial 10 size 1000,800
set output 'inDeg.wikiInDeg.png'
plot 	"inDeg.wikiInDeg.tab" using 1:2 title "" with linespoints pt 6
