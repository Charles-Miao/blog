
# coding: utf-8

# In[31]:


import pandas as pd
RelativeTestTime=pd.Series([0.951289398,0.954564061,0.954564061,0.955382726,0.972574703,0.973393369,0.973393369,0.976258698,0.983626688,0.99713467,1.0998772])
MemoryScore=pd.Series([5.9,5.9,5.5,5.9,5.9,7.4,5.9,7.7,5.5,5.9,5.9])
CpuScore=pd.Series([7.1,6.9,6.2,6.8,6.8,6.9,6.8,7.5,7.1,6.6,6.8])
DiskScore=pd.Series([5.9,5.9,5.9,5.9,5.9,5.9,5.9,5.9,5.9,5.9,5.9])
CPUTemperature=pd.Series([52.6,41.7,62.36,41.8,42.5,63.9,39.9,59.9,88.2,68.8,35.7])
CPULoading=pd.Series([9.6,12.6,15.2,25.1,24.3,30.8,16.8,5.3,24.6,14.3,33.9])
MemoryAvailable=pd.Series([2.31,2.02,1.83,1.26,1.71,1.03,1.68,5.55,0.7,2.05,1.86])


# In[32]:


RelativeTestTime.corr(MemoryScore)


# In[33]:


RelativeTestTime.corr(CpuScore)


# In[34]:


RelativeTestTime.corr(DiskScore)


# In[35]:


RelativeTestTime.corr(CPUTemperature)


# In[36]:


RelativeTestTime.corr(CPULoading)


# In[37]:


RelativeTestTime.corr(MemoryAvailable)


# In[38]:


MemoryScore.corr(MemoryAvailable)


# In[39]:


CpuScore.corr(CPUTemperature)


# In[40]:


CpuScore.corr(CPULoading)


# In[41]:


CPULoading.corr(CPUTemperature)

