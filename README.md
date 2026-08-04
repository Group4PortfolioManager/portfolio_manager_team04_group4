This is a repo for the CSF project with Group 4.

<h1 align="center">PortFolio</h1>

<p align="center">
  <strong>An open-source, portfolio manager.</strong>
</p>

## Overview

## Features

## Stack

## How to Run
### Installing the Prerequisites
First, you need to clone the repository:

```sh
git clone https://github.com/Group4PortfolioManager/portfolio_manager_team04_group4.git
```
After cloning, you need to install these Python Packages

cd ./frontend/
npm install

### Envirorment Variables

Create a `.env` file at the root of the project and set these values:

|Variable|Value|
|---|---|
|`db_host`|The name of the host the database is being hosted on (Ex: `localhost`)|
|`db_user`|A username belonging to the profile who has access to the hosted database|
|`db_password`|The password of the user given in `db_user`|
|`db_name`|`portfolio_tracker`|


### Starting the App
First, run this command from the root repository to start the backend:
```sh
python -m app.main
```
In a separate terminal, go to the `frontend` folder:
```sh
cd ./frontend/
```
And run this command to start the frontend:
```sh
npm run dev
```
The link of the app will be given in the separate terminal (Ex: http://localhost:3000/).

## Screenshots