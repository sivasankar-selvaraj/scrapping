Scraping Application
================================================
This is a custom application not a generic, because it's scrap the specific url based on class and id of pagecontent.


Running
=======
To run this application by using following command:

	1) scrap all product data
		
		(venv) $ python scrap.py url 

	2) scrap products links
		
		Call get_products_link(link_file) 

		link_file - file with catogory links

	3) scrap product data

		Call get_products(link_file) 

		link_file - file with products_link

Output
======
	category_links.txt - all main category url

	product_links.txt - all products url
	
	product.json - all product data


Note : Please change the file name or filepath in config.cnf
