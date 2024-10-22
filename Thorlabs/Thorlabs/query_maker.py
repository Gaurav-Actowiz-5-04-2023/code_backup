import pymysql
import db_config as db
from datetime import datetime

date = datetime.now()
month = date.strftime('%B')

query = f'''/*
SQLyog Ultimate v13.1.1 (64 bit)
MySQL - 8.0.21 : Database - ics_master_db_v1_Thorlabs_{month}
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`ics_master_db_v1_Thorlabs_{month}` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `ics_master_db_v1_Thorlabs_{month}`;

/*Table structure for table `asset_table` */

DROP TABLE IF EXISTS `asset_table`;

CREATE TABLE `asset_table` (
  `id` int NOT NULL AUTO_INCREMENT,
  `vendor_id` varchar(50) DEFAULT NULL,
  `hash_key` varchar(255) NOT NULL,
  `sku` varchar(50) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `source` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `sha256` varchar(256) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `media_type` varchar(255) DEFAULT NULL,
  `length` varchar(255) DEFAULT NULL,
  `file_name` varchar(255) DEFAULT NULL,
  `download_path` varchar(255) DEFAULT NULL,
  `is_main_image` tinyint(1) DEFAULT '0',
  `status` varchar(20) DEFAULT 'pending',
  PRIMARY KEY (`id`),
  UNIQUE KEY `vendor_id` (`vendor_id`,`source`,`hash_key`)
) ENGINE=InnoDB AUTO_INCREMENT=34752 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Table structure for table `pricing_table` */

DROP TABLE IF EXISTS `pricing_table`;

CREATE TABLE `pricing_table` (
  `id` int NOT NULL AUTO_INCREMENT,
  `vendor_id` varchar(50) DEFAULT NULL,
  `hash_key` varchar(255) NOT NULL,
  `sku` varchar(50) DEFAULT NULL,
  `min_qty` int DEFAULT '1',
  `price` float DEFAULT NULL,
  `price_string` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '',
  `currency` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `vendor_id` (`vendor_id`,`price`,`price_string`,`min_qty`,`hash_key`)
) ENGINE=InnoDB AUTO_INCREMENT=73401 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Table structure for table `product_table` */

DROP TABLE IF EXISTS `product_table`;

CREATE TABLE `product_table` (
  `id` int NOT NULL AUTO_INCREMENT,
  `vendor_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `hash_key` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `vendor_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `sku` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `pdp_url` varchar(255) DEFAULT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `category` json DEFAULT NULL,
  `uom` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT 'each',
  `sku_unit` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT 'item',
  `sku_quantity` int DEFAULT '1',
  `quantity_increment` int DEFAULT '1',
  `pack_label` varchar(100) DEFAULT NULL,
  `available_to_checkout` tinyint(1) DEFAULT '1',
  `in_stock` tinyint(1) DEFAULT '1',
  `estimated_lead_time` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `description` text,
  `description_html` longtext,
  `manufacturer` varchar(100) DEFAULT NULL,
  `mpn` varchar(50) DEFAULT NULL,
  `attributes` json DEFAULT NULL,
  `features` json DEFAULT NULL,
  `_scrape_metadata` json DEFAULT NULL,
  `status` varchar(20) DEFAULT 'pending',
  PRIMARY KEY (`id`),
  UNIQUE KEY `vendor_id` (`vendor_id`,`hash_key`)
) ENGINE=InnoDB AUTO_INCREMENT=73434 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Table structure for table `site_map_link_table` */

DROP TABLE IF EXISTS `site_map_link_table`;

CREATE TABLE `site_map_link_table` (
  `id` int NOT NULL AUTO_INCREMENT,
  `vendor_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `vendor_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `product_urls` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `meta_data` json DEFAULT NULL,
  `status` varchar(50) DEFAULT 'pending',
  PRIMARY KEY (`id`),
  UNIQUE KEY `product_urls` (`product_urls`)
) ENGINE=InnoDB AUTO_INCREMENT=75197 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
'''


open('D:\Data\gaurav\projects\Thorlabs\Thorlabs.sql', 'w').write(query)
