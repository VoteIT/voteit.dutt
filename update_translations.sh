 #!/bin/bash
 #You need lingua and gettext installed to run this
 
 echo "Updating voteit.dutt.pot"
 pot-create -d voteit.dutt -o voteit/dutt/locale/voteit.dutt.pot .
 echo "Merging Swedish localisation"
 msgmerge --update voteit/dutt/locale/sv/LC_MESSAGES/voteit.dutt.po voteit/dutt/locale/voteit.dutt.pot
 echo "Updated locale files"
 