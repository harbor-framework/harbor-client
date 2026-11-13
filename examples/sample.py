from harbor_client import HarborAPIClient
from harbor_client.types import (
    JobsListRequestScope,
    JobsListRequestAccess,
    JobsListRequestArchive,
    JobsListRequestSort,
)

client = HarborAPIClient(
    harbor_api_version="YOUR_HARBOR_API_VERSION",
)
response = client.jobs.list(
    page_size="page_size",
    page_token="page_token",
    offset="offset",
    search="search",
    agents="agents",
    providers="providers",
    models="models",
    date_="date",
    scope="my",
    shared_with_organization_id="7FaADc39-CD81-dA6F-CB26-8E0278969Ada",
    datasets="datasets",
    access="owned",
    owner_organization_id="3854E4f2-aaD5-156D-0AF9-aeA9CeDf2e3e",
    date_from="date_from",
    date_to="date_to",
    created_by="4eDc7C70-005C-ecBD-810A-B7EEDe2c0Ab8",
    archive="current",
    sort="importance",
)
for item in response:
    print(item)
# alternatively, you can paginate page-by-page
for page in response.iter_pages():
    print(page)
