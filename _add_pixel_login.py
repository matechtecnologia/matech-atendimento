with open("templates/login.html", "r", encoding="utf-8") as f:
    c = f.read()

pixel_e_tracking = """
<!-- Meta Pixel Code -->
<script>
!function(f,b,e,v,n,t,s)
{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '1797761131556226');
fbq('track', 'PageView');

// Se veio de cadastro (?lead=1), dispara o evento Lead
(function() {
    var url = new URL(window.location.href);
    if (url.searchParams.get('lead') === '1') {
        fbq('track', 'Lead');
        // Limpa o parametro depois de disparar
        url.searchParams.delete('lead');
        window.history.replaceState({}, '', url.toString());
    }
})();
</script>
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id=1797761131556226&ev=PageView&noscript=1"
/></noscript>
<!-- End Meta Pixel Code -->
"""

if "1797761131556226" not in c:
    c = c.replace("</head>", pixel_e_tracking + "\n</head>", 1)
    with open("templates/login.html", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - Pixel + Lead tracking no login")
else:
    print("AVISO - ja estava")
