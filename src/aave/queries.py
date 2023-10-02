

# borrows_or_supplies_query = f"""
#     {{
#         {data_type}(
#             where: {{reserve_: {{symbol: "{token_symbol}"}}, id_gt: "{last_id}"}}
#             orderBy: timestamp
#             orderDirection: asc
#             first: 1000
#         ){{
#             id
#             timestamp
#             reserve {{
#                 stableBorrowRate
#                 variableBorrowRate
#                 utilizationRate
#                 lastUpdateTimestamp
#             }}
#         }}
#     }}
#     """

reserves_query = """
{
  reserves(
    first:1000,
    orderBy : id
  ){
    id
    symbol
    name
    paramsHistory{
      id
      timestamp
      utilizationRate
      stableBorrowRate
      variableBorrowRate
    }
  }
}
"""