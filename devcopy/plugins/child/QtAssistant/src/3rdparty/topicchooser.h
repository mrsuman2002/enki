'''***************************************************************************
**
** Copyright (C) 2009 Nokia Corporation and/or its subsidiary(-ies).
** All rights reserved.
** Contact: Nokia Corporation (qt-info@nokia.com)
**
** This file is part of the Qt Assistant of the Qt Toolkit.
**
** $QT_BEGIN_LICENSE:LGPL$
** No Commercial Usage
** This file contains pre-release code and may not be distributed.
** You may use self file in accordance with the terms and conditions
** contained in the Technology Preview License Agreement accompanying
** self package.
**
** GNU Lesser General Public License Usage
** Alternatively, file may be used under the terms of the GNU Lesser
** General Public License version 2.1 as published by the Free Software
** Foundation and appearing in the file LICENSE.LGPL included in the
** packaging of self file.  Please review the following information to
** ensure the GNU Lesser General Public License version 2.1 requirements
** will be met: http:#www.gnu.org/licenses/old-licenses/lgpl-2.1.html.
**
** In addition, a special exception, gives you certain additional
** rights.  These rights are described in the Nokia Qt LGPL Exception
** version 1.1, in the file LGPL_EXCEPTION.txt in self package.
**
** If you have questions regarding the use of self file, contact
** Nokia at qt-info@nokia.com.
**
**
**
**
**
**
**
**
** $QT_END_LICENSE$
**
***************************************************************************'''

#ifndef TOPICCHOOSER_H
#define TOPICCHOOSER_H

#include "ui_topicchooser.h"

#include <QUrl>
#include <QMap>
#include <QString>

#include <QtGui/QDialog>

QT_BEGIN_NAMESPACE

class TopicChooser : public QDialog
    Q_OBJECT

public:
    TopicChooser(QWidget *parent, &keyword,
         QMap<QString, &links)

    QUrl link() const;    
    
private:
    Ui.TopicChooser ui
    QMap<QString, m_links


QT_END_NAMESPACE

#endif # TOPICCHOOSER_H
