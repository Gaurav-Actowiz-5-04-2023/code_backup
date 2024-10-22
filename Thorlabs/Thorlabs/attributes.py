import pandas as pd

html_elements = '''<table cellspacing="0" class="SpecTable" width="375">
<thead>
<tr align="center">
<th style="text-align: left;">Item #</th>
<th colspan="2">ADT-6</th>
<th colspan="2"> ADG-6</th>
</tr>
<tr align="center">
<td style="text-align: left;"><strong>Material</strong></td>
<td colspan="2">Rutile</td>
<td>Gadolinium Gallium<br> Garnet</td>
</tr>
<tr align="center">
<td style="text-align: left;"><strong>Index of Refraction<sup>a,b</sup></strong></td>
<td colspan="2"><a href="images/tabimages/Rutile_Sellmeier_G2-780.gif" onclick="return hs.expand(this,{wrapperClassName: 'highslide-no-border'})"><img src="https://www.thorlabs.com/images/TabImages/Rutile_Sellmeier_Icon.gif" border="0" alt="" width="20" height="16"></a></td>
<td colspan="2"><a href="images/tabimages/GGG_Sellmeier_G1-780.gif" onclick="return hs.expand(this,{wrapperClassName: 'highslide-no-border'})"><img src="https://www.thorlabs.com/images/TabImages/GGG_Sellmeier_Icon.gif" border="0" alt="" width="20" height="16"></a></td>
</tr>
<tr align="center">
<td style="text-align: left;"><strong>Sellmeier Equation<sup>a,b</sup></strong></td>
<td colspan="2"><a href="images/TabImages/Rutile_Sellmeier_Equation.png" onclick="return hs.expand(this, {wrapperClassName: 'highslide-no-border', captionText:'Rutile Index of Refraction, Extraordinary (top) and Ordinary (bottom) Rays. Valid for 0.612 to 4.449 µm. Equation takes wavelength in nanometers.'})"><img src="https://www.thorlabs.com/images/TabImages/info_icon.png" border="0" alt="Icon" width="15" height="15"><br></a></td>
<td colspan="2"><a href="images/TabImages/GGG_Sellmeier_Equation.png" onclick="return hs.expand(this, {wrapperClassName: 'highslide-no-border', captionText:'Gadolinium Gallium Garnet Index of Refraction, Valid for 0.36 to 6.0 µm. Equation takes wavelength in microns.'})"><img src="https://www.thorlabs.com/images/TabImages/info_icon.png" border="0" alt="Icon"></a></td>
</tr>
<tr align="center">
<td style="text-align: left;"><strong>L<sup>c</sup></strong></td>
<td colspan="4">6.0 mm</td>
</tr>
<tr align="center">
<td style="text-align: left;"><strong>X<sup>c</sup></strong></td>
<td colspan="4">8.5 mm</td>
</tr>
<tr align="center">
<th colspan="5" style="text-align: left;">Index of Refraction for Select Wavelengths</th>
</tr>
<tr align="center">
<td style="text-align: left;" class="subhead"><strong>λ</strong></td>
<td class="subhead">n<sub>o</sub></td>
<td class="subhead">n<sub>e</sub></td>
<td colspan="2" class="subhead">n</td>
</tr>
</thead>
<tbody>
<tr align="center">
<td style="text-align: left;">633 nm</td>
<td>2.583</td>
<td>2.874</td>
<td colspan="2">1.965</td>
</tr>
<tr align="center">
<td style="text-align: left;">830 nm</td>
<td>2.516</td>
<td>2.781</td>
<td colspan="2">1.951</td>
</tr>
<tr align="center">
<td style="text-align: left;">1064 nm</td>
<td>2.482</td>
<td>2.734</td>
<td colspan="2">1.944</td>
</tr>
<tr align="center">
<td style="text-align: left;">1550 nm</td>
<td>2.449</td>
<td>2.691</td>
<td colspan="2">1.936</td>
</tr>
</tbody>
</table>'''

html_df = pd.read_html(html_elements)

print(html_df)