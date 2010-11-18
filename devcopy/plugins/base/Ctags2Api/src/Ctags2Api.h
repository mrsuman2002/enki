'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Base Plugins
** FileName  : Ctags2Api.h
** Date      : 2008-01-14T00:39:52
** License   : GPL
** Comment   : This header has been automatically generated, you are the original author, co-author, free to replace/append with your informations.
** Home Page : http:#www.monkeystudio.org
**
    Copyright (C) 2005 - 2008  Filipe AZEVEDO & The Monkey Studio Team

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with self program; if not, to the Free Software
    Foundation, Inc., Franklin St, Floor, Boston, 02110-1301  USA
**
***************************************************************************'''
#ifndef CTAGS2API_H
#define CTAGS2API_H

#include <pluginsmanager/BasePlugin.h>

class Ctags2Api : public BasePlugin
    Q_OBJECT
    Q_INTERFACES( BasePlugin )
protected:    
    void fillPluginInfos()
    virtual bool install()
    virtual bool uninstall()
public:

protected slots:
    void UICtags2Api_show()
    


#endif # CTAGS2API_H