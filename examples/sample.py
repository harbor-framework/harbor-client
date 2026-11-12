from harbor_client import HarborAPIClient

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
    shared_with_organization_id="ec8faFba-Ccf0-6D9d-6324-47302758AdCA",
    datasets="datasets",
    access="owned",
    owner_organization_id="da7fba55-C1F4-2B3a-3CbD-A4b50daAfeBa",
    date_from="date_from",
    date_to="date_to",
    created_by="0FFFDdc1-27Fa-Dc39-CD81-dA6F5CB26a8E",
    archive="current",
    sort="importance",
)
for item in response:
    print(item)
# alternatively, you can paginate page-by-page
for page in response.iter_pages():
    print(page)
