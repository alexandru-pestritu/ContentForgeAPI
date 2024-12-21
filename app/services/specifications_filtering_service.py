from collections import defaultdict
from typing import List, Dict, Any, Tuple
from pydantic import BaseModel

from app.schemas.product import ProductResponse
from app.services.settings_service import SettingsService

class SpecificationsFilteringService:
    def __init__(self, max_specs: int = 10):
        self.max_specs = SettingsService.get_setting_value("max_specs")

    def filter_specifications(self, products: List[ProductResponse]) -> List[ProductResponse]:
        """
        Filter and select the top specifications for each product.

        Args:
            products: A list of ProductResponse instances.

        Returns:
            A list of ProductResponse instances with updated specifications.
        """
        product_specs_list = []

        for product in products:
            product_specs_list.append(product.specifications)

        spec_name_mapping = {
        }

        standardized_products = self.standardize_spec_names(product_specs_list, spec_name_mapping)

        final_specs_list = self.process_products(standardized_products, self.max_specs)

        for idx, product in enumerate(products):
            product.specifications = final_specs_list[idx]

        return products

    def standardize_spec_names(self, products: List[Dict[str, Any]], spec_name_mapping: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Standardize specification names across products.

        Args:
            products: A list of dictionaries, each representing a product's specifications.
            spec_name_mapping: A dictionary mapping original spec names to standardized names.

        Returns:
            A list of products with standardized specification names.
        """
        standardized_products = []
        for product in products:
            standardized_product = {}
            for spec, value in product.items():
                standardized_spec = spec_name_mapping.get(spec, spec)
                standardized_product[standardized_spec] = value
            standardized_products.append(standardized_product)
        return standardized_products

    def process_products(self, products: List[Dict[str, Any]], max_specs: int) -> List[Dict[str, Any]]:
        """
        Process a list of products to select and order their top specifications.

        Args:
            products: A list of dictionaries, each representing a product's specifications.
            max_specs: The maximum number of specifications to select.

        Returns:
            A list of dictionaries with selected and ordered specifications for each product.
        """
        total_products = len(products)
        spec_frequency, spec_variability = self.analyze_specifications(products)
        spec_relevance = self.calculate_relevance(spec_frequency, spec_variability, total_products)
  
        specs_to_place_last = SettingsService.get_setting_value("specs_to_place_last").split(",")
        spec_order = self.get_ordered_spec_list(spec_relevance, specs_to_place_last)
        final_specs_list = self.select_top_specs(products, spec_order, max_specs)
        return final_specs_list

    def analyze_specifications(self, products: List[Dict[str, Any]]) -> Tuple[Dict[str, int], Dict[str, set]]:
        """
        Analyze specifications to calculate frequency and variability.

        Args:
            products: A list of dictionaries, each representing a product's specifications.

        Returns:
            spec_frequency: A dictionary with specifications as keys and their frequency counts as values.
            spec_variability: A dictionary with specifications as keys and sets of unique values as values.
        """
        spec_frequency = defaultdict(int)
        spec_variability = defaultdict(set)
        for product in products:
            for spec, value in product.items():
                spec_frequency[spec] += 1
                if value is not None:
                    spec_variability[spec].add(value)
        return spec_frequency, spec_variability

    def calculate_relevance(self, spec_frequency: Dict[str, int], spec_variability: Dict[str, set], total_products: int) -> Dict[str, float]:
        """
        Calculate the relevance score for each specification.

        Args:
            spec_frequency: A dictionary of specification frequencies.
            spec_variability: A dictionary of specification variability.
            total_products: The total number of products.

        Returns:
            spec_relevance: A dictionary with specifications as keys and relevance scores as values.
        """
        frequency_percentage = SettingsService.get_setting_value("spec_relevance_percentage")
        variability_percentage = SettingsService.get_setting_value("spec_variability_percentage")
        spec_relevance = {}
        for spec in spec_frequency:
            frequency_score = spec_frequency[spec] / total_products 
            variability_score = len(spec_variability[spec]) / total_products  
            spec_relevance[spec] = (frequency_percentage * frequency_score) + (variability_percentage * variability_score)
        return spec_relevance

    def get_ordered_spec_list(self, spec_relevance: Dict[str, float], specs_to_place_last: List[str]) -> List[str]:
        """
        Generate an ordered list of specifications based on relevance scores,
        placing specified specs at the end.

        Args:
            spec_relevance: A dictionary with specifications as keys and relevance scores as values.
            specs_to_place_last: A list of specifications to place at the end.

        Returns:
            A list of specifications ordered by relevance, with specified specs at the end.
        """
        main_specs = {spec: relevance for spec, relevance in spec_relevance.items() if spec not in specs_to_place_last}
        last_specs = {spec: relevance for spec, relevance in spec_relevance.items() if spec in specs_to_place_last}

        ordered_main_specs = sorted(main_specs, key=main_specs.get, reverse=True)
        ordered_last_specs = sorted(last_specs, key=last_specs.get, reverse=True)

        return ordered_main_specs + ordered_last_specs

    def select_top_specs(self, products: List[Dict[str, Any]], spec_order: List[str], max_specs: int) -> List[Dict[str, Any]]:
        """
        Select the top specifications for each product based on the ordered spec list.

        Args:
            products: A list of dictionaries, each representing a product's specifications.
            spec_order: An ordered list of specifications.
            max_specs: The maximum number of specifications to select.

        Returns:
            A list of dictionaries with selected specifications for each product.
        """
        final_specs_list = []
        for product in products:
            specs = {}
            for spec in spec_order:
                if spec in product and product[spec] is not None:
                    specs[spec] = product[spec]
                if len(specs) >= max_specs:
                    break
            final_specs_list.append(specs)
        return final_specs_list
