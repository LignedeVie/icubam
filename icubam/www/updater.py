from  absl import logging

from icubam import time_utils
from icubam.db import store
from icubam.www.handlers import home
from icubam.www import token


def apply_default(data: dict, value: int, prefix: str):
  """Applies default values to undefined entries of a dict matching a prefix."""
  for k in data:
    if data[k] is None and k.startswith(prefix):
      data[k] = value


class Updater:
  """Helper class for dealing with updating the counts."""

  ROUTE = '/update'

  def __init__(self, config, db):
    self.config = config
    self.db = db
    self.token_encoder = token.TokenEncoder(self.config)

  def get_url(self, icu_id: str, icu_name: str) -> str:
    return "{}{}?id={}".format(
      self.config.server.base_url,
      self.ROUTE.strip('/'),
      self.token_encoder.encode_icu(icu_id, icu_name))

  def get_urls(self):
    result = []
    for user in self.db.get_users():
      for icu in user.icus:
        result.append(self.get_url(icu.icu_id, icu.name))
    return result

  def get_icu_data_by_id(self, icu_id, locale=None, def_val=0):
    """Returns the dictionary of counts for the given icu."""
    bed_count = self.db.get_bed_count_for_icu(icu_id)
    print(icu_id)
    print(bed_count)
    bed_count = bed_count if bed_count is not None else store.BedCount()
    # In case there is a weird corner case, we don't want to crash the form:
    last_update = bed_count.last_modified
    data = store.to_dict(bed_count)
    apply_default(data, value=def_val, prefix='n_')
    data['since_update'] = time_utils.localewise_time_ago(last_update, locale)
    data['home_route'] = home.HomeHandler.ROUTE
    data['update_route'] = self.ROUTE
    return data
