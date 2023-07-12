


#Importing the Dependecies first 
import requests
from requests.exceptions import RequestException

from schemas import HodlHodlOfferBase, HodlHodlUserBase


class Scraper:
    def __init__(self, **kwargs):
        self.proxy = kwargs.get("proxy")
        # Creating session for making HTTP requests
        self.requester = requests.Session() 
        self.total_offer_percent_to_scrape = kwargs.get("total_offer_percent_to_scrape", 100)

    def get_currency_list(self):
        """
        Fetches the list of available currencies from Hodl Hodl API.

        Returns:
            list: List of currency codes.
        """
        url = 'https://hodlhodl.com/api/frontend/currencies'
        currency_list = []
        try:
            response = self.requester.get(url)
            response.raise_for_status()  
            # Raising an exception if the HTTP request is unsuccessful
            currencies = response.json()
            currency_list = [curr.get("code") for curr in currencies.get("currencies")]
        except RequestException as e:
            print(f"Error fetching currency list: {e}")
        return currency_list

    def get_and_post_offers(self, curr, trading_type):
        """
        Fetches and posts offers for a given currency and trading type.

        Args:
            curr (str): Currency code.
            trading_type (str): Trading type, either "buy" or "sell".
        """
        url = f"https://hodlhodl.com/api/frontend/offers?filters[currency_code]={curr}&pagination[offset]=0&filters[side]={trading_type}&facets[show_empty_rest]=true&facets[only]=false&pagination[limit]=100"
        try:
            response = self.requester.get(url)
            response.raise_for_status() 
            # this raises an exception if the HTTP request is unsuccessful
            offers = response.json().get("offers")
            for offer in offers:
                offer_info = self.create_offer_data(offer)
                seller_info = self.create_seller_data(offer)
                self.post_data_to_api(seller_info, offer_info)
        except RequestException as e:
            print(f"Error fetching offers: {e}")

    @staticmethod
    def create_offer_data(offer):
        """
        Creates an instance of HodlHodlOfferBase from the offer data.

        Args:
            offer (dict): Offer data.

        Returns:
            HodlHodlOfferBase: Instance of HodlHodlOfferBase.
        """
        return HodlHodlOfferBase(
            offer_identifier=offer.get("id"),
            fiat_currency=offer.get("asset_code"),
            country_code=offer.get("country_code"),
            trading_type_name=offer.get("side"),
            trading_type_slug=offer.get("side"),
            payment_method_name=offer.get("payment_methods")[0].get("type") if offer.get("payment_methods") else None,
            payment_method_slug=offer.get("payment_methods")[0].get("type") if offer.get("payment_methods") else None,
            description=offer.get("description"),
            currency_code=offer.get("currency_code"),
            coin_currency=offer.get("currency_code"),
            price=offer.get("price"),
            min_trade_size=offer.get("min_amount"),
            max_trade_size=offer.get("max_amount"),
            site_name='hodlhodl',
            margin_percentage=0,
            headline=''
        )

    @staticmethod
    def create_seller_data(offer):
        """
        Creates an instance of HodlHodlUserBase from the offer data.

        Args:
            offer (dict): Offer data.

        Returns:
            HodlHodlUserBase: Instance of HodlHodlUserBase.
        """
        return HodlHodlUserBase(
            username=offer.get("trader").get("login"),
            feedback_score=offer.get("trader").get("rating") or 0,
            completed_trades=offer.get("trader").get("trades_count"),
            seller_url=offer.get("trader").get("url"),
            profile_image='',
            trade_volume=0
        )

    def post_data_to_api(self, seller_info, offer_info):
        """
        Posts the offer and seller data to an API.

        Args:
            seller_info (HodlHodlUserBase): Seller data.
            offer_info (HodlHodlOfferBase): Offer data.
        """
        data = {
            "user": seller_info.dict(),
            "offer": offer_info.dict(),
        }

        cc = offer_info.dict()["country_code"]
        if cc == "Global":
            cc = 'GL'

        params = {
            "country_code": cc,
            "payment_method": offer_info.dict()["payment_method_name"],
            "payment_method_slug": offer_info.dict()["payment_method_slug"],
        }

        try:
            print(params, data)
        except RequestException as e:
            print(f"Error posting data to API: {e}")

    def scrape_hodlhodl_offers(self):
        """
        Initiates the process of scraping Hodl Hodl offers.
        """
        currencies_list = self.get_currency_list()
        for curr in currencies_list:
            for trading_type in ["buy", "sell"]:
                self.get_and_post_offers(curr, trading_type)

#Added a new scrape_hodlhodl_offers() method as an entry point to initiate the scraping process.
if __name__ == "__main__":
    scraper = Scraper()
    scraper.scrape_hodlhodl_offers()
