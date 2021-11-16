import Glean from "@mozilla/glean/web";

import { pageView as pageViewPing } from "./generated/pings.js";
import * as pageMetrics from "./generated/page.js";

Glean.setLogPings(true);
Glean.initialize("moz-bedrock", true);

pageMetrics.viewed.set();
pageMetrics.id.set(Mozilla.Analytics.getPageId(location.pathname));
pageViewPing.submit();

