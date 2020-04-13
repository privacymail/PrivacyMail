import React from "react";

const FAQ = () => {
    return (
        <div className="faq">
            <h1>Häufige Fragen</h1>
            <p>
                Auf dieser Seite versuchen wir, einige häufig gestellte Fragen zu beantworten. Wenn Du eine Frage hast,
                die hier nicht beantwortet wird, melde Dich gerne bei uns.
            </p>

            <h2>Für Nutzer*innen</h2>
            <h3>Was ist PrivacyMail?</h3>
            <p>
                PrivacyMail ist ein automatisches System das dir dabei hilft, herauszufinden, ob die Firmen, die dir
                Newsletter schicken, Tracking-Technologien nutzen, um herauszufinden welche Mails du liest und welche
                Links du anklickst. Es soll dir dabei helfen, dich zu informieren und Transparenz in diesen oft
                intransparenten Bereich bringen. PrivacyMail ist außerdem auch ein Forschungswerkzeug, betrieben durch
                das{" "}
                <a href="https://seemoo.de/" target="blank">
                    Secure Mobile Networking Lab
                </a>{" "}
                an der TU Darmstadt in Deutschland.
            </p>

            <h3>Was kostet PrivacyMail? Wie verdient ihr Geld?</h3>
            <p>
                PrivacyMail ist ein nicht-kommerzielles Forschungsprojekt. Die laufenden Kosten werden aktuell vom{" "}
                <a href="https://seemoo.de/" target="blank">
                    Secure Mobile Networking Lab (SEEMOO)
                </a>{" "}
                an der TU Darmstadt übernommen. Die Weiterentwicklung geschieht durch das SEEMOO-Team, Studierende (als
                Teil von Projekten oder Abschlussarbeiten), und Freiwilligen. PrivacyMail ist Open Source und wird
                niemals Geld für die Nutzung verlangen oder Werbung zeigen. Die gesammelten Daten werden für
                Forschungszwecke ausgewertet (siehe nächste Frage).
            </p>

            <h3>Was passiert mit den gesammelten Daten?</h3>
            <p>
                Um eine Sache von Anfang an klarzustellen: <b>Wir sammeln keine Daten über Dich!</b> Die Daten, die wir
                sammeln, beziehen sich ausschließlich auf die Newsletter, die Du und andere bei uns angemeldet haben.
            </p>
            <p>
                Wir analysieren ankommende eMails, um die auf der Webseite gezeigten Ergebnisse zu erzeugen, und
                kombinieren sie mit Daten aus{" "}
                <a href="https://privacyscore.org" target="blank">
                    anderen Projekten
                </a>{" "}
                um ein klareres Bild der Online-Tracking-Industrie zu erhalten. Die Daten werden auf Anfrage mit anderen
                Forschenden geteilt, oder als Teil größerer Datensätze veröffentlicht, um{" "}
                <a href="https://de.wikipedia.org/wiki/Reproduzierbarkeit#Wissenschaft" target="blank">
                    reproduzierbare Forschung
                </a>{" "}
                zu ermöglichen. Wenn Du Forschung betreibst und mit unseren Daten arbeiten möchtest, melde dich gerne
                bei uns.
            </p>

            <h3>In welchem Zusammenhang stehen PrivacyMail und PrivacyScore?</h3>
            <p>
                Einige Mitglieder des PrivacyMail-Teams arbeiten auch an{" "}
                <a href="https://privacyscore.org" target="blank">
                    PrivacyScore
                </a>
                . Ein Teil der Infrastruktur und Technologie wird von beiden Projekten gemeinsam genutzt. Bis darauf
                sind die beiden Projekte allerdings unabhängig.{" "}
            </p>

            <h2>Für Newsletter-Betreiber</h2>
            <h3>Warum untersucht Ihr meinen Newsletter?</h3>
            <p>Wir untersuchen alle Newsletter, die von Nutzer*innen angemeldet wurden.</p>

            <h3>Könnt Ihr mich aus Eurem System entfernen?</h3>
            <p>
                Wenn Sie nicht wollen, dass wir Ihren Newsletter untersuchen, schicken Sie uns bitte eine eMail. Wir
                werden dann alle Abonnements beenden und dafür sorgen, dass keine neuen angelegt werden können.{" "}
                <strong>
                    Wir weisen ausdrücklich darauf hin, dass dies keinen Einfluss auf existierende Ergebnisse hat (sie
                    werden nicht entfernt). Die Entscheidung, sich aus dem System entfernen zu lassen, wir öffentlich
                    dokumentiert.
                </strong>{" "}
                Nutzer*innen, die sich für Ihren Newsletter interessieren, werden mit einer Nachricht darauf hingewisen,
                dass Sie darum geben haben, aus dem System entfernt zu werden, und können die historischen Ergebnisse
                betrachten. Alle auf diese Art deaktivierten Newsletter werden in einer öffentlichen Liste geführt.
            </p>
        </div>
    );
};

export default FAQ;
